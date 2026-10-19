import { useGraphics } from "../hooks/useGraphics";
import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { CameraPreset, BallTrajectory } from "../types";
import { BALL_TRAJECTORIES } from "../data/mockData";
import { Eye, Crosshair, Compass, ShieldAlert, Layers, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

function disposeObject(object: THREE.Object3D) {
  object.traverse(child => {
    const mesh = child as THREE.Mesh;
    mesh.geometry?.dispose();
    const materials = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
    materials.forEach(material => { Object.values(material).forEach(value => { if(value instanceof THREE.Texture) value.dispose(); }); material.dispose(); });
    if(child instanceof THREE.DirectionalLight || child instanceof THREE.SpotLight) child.shadow.dispose();
  });
}

export interface Stadium3DProps {
  initialCamera?: CameraPreset;
  selectedTrajectory?: BallTrajectory | null;
  onSelectTrajectory?: (traj: BallTrajectory) => void;
  showHeatmap?: boolean;
  filterPhase?: "All" | "Powerplay" | "Middle" | "Death";
  filterBowlerType?: "All" | "Pace" | "Spin";
  className?: string;
}

export const StadiumWebGL: React.FC<Stadium3DProps> = ({
  initialCamera = "broadcast",
  selectedTrajectory,
  onSelectTrajectory,
  showHeatmap = true,
  filterPhase = "All",
  filterBowlerType = "All",
  className = "w-full h-full"
}) => {
  const { preferences, update } = useGraphics();
  const [contextLost,setContextLost] = useState(false);
  const rotateRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentCameraMode, setCurrentCameraMode] = useState<CameraPreset>(initialCamera);
  const [showPitchGrid, setShowPitchGrid] = useState<boolean>(true);

  // References for Three.js instance
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const trajectoriesGroupRef = useRef<THREE.Group | null>(null);
  const heatmapGroupRef = useRef<THREE.Group | null>(null);
  const targetCameraPos = useRef<THREE.Vector3>(new THREE.Vector3(0, 45, 65));
  const targetLookAt = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));
  const currentLookAt = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));

  // Camera presets coordinates
  const cameraConfigs: Record<CameraPreset, { pos: [number, number, number]; lookAt: [number, number, number] }> = {
    broadcast: { pos: [0, 42, 60], lookAt: [0, 0, 0] },
    top_down: { pos: [0, 80, 0.01], lookAt: [0, 0, 0] },
    bowler_view: { pos: [0, 3.8, -18], lookAt: [0, 1.2, 10] },
    batter_view: { pos: [0, 2.4, 12.5], lookAt: [0, 2.0, -14] },
    pitch_heatmap: { pos: [10, 8, 0], lookAt: [0, 0.5, 0] },
    stadium_orbit: { pos: [50, 32, 50], lookAt: [0, 0, 0] }
  };

  const handleCameraChange = (preset: CameraPreset) => {
    setCurrentCameraMode(preset);
    rotateRef.current = preset === "stadium_orbit";
    const cfg = cameraConfigs[preset];
    targetCameraPos.current.set(...cfg.pos);
    targetLookAt.current.set(...cfg.lookAt);
    if (preset === "stadium_orbit") {
      rotateRef.current = true;
    } else {
      rotateRef.current = false;
    }
  };

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = Math.max(1,container.clientWidth);
    const height = Math.max(1,container.clientHeight);

    // 1. Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0xf7f5ed);
    scene.fog = new THREE.FogExp2(0xf7f5ed, 0.008);

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    cameraRef.current = camera;
    const initialCfg = cameraConfigs[currentCameraMode];
    camera.position.set(...initialCfg.pos);
    targetCameraPos.current.set(...initialCfg.pos);
    targetLookAt.current.set(...initialCfg.lookAt);
    currentLookAt.current.set(...initialCfg.lookAt);
    camera.lookAt(currentLookAt.current);

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: preferences.quality !== "BALANCED", powerPreference: "low-power" });
    rendererRef.current = renderer;
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, preferences.quality === "ULTRA" ? 2 : preferences.quality === "HIGH" ? 1.5 : 1));
    renderer.shadowMap.enabled = preferences.shadows;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.replaceChildren(renderer.domElement);

    // 4. Lighting Environment
    const ambientLight = new THREE.AmbientLight(0x1a2638, 1.2);
    scene.add(ambientLight);

    const mainFloodlight = new THREE.DirectionalLight(0xd6eeff, 2.4);
    mainFloodlight.position.set(35, 60, 35);
    mainFloodlight.castShadow = preferences.shadows;
    mainFloodlight.shadow.mapSize.width = 2048;
    mainFloodlight.shadow.mapSize.height = 2048;
    scene.add(mainFloodlight);

    const fillLight = new THREE.DirectionalLight(0x46664f, 0.6);
    fillLight.position.set(-35, 45, -35);
    fillLight.visible = preferences.lights;
    mainFloodlight.visible = preferences.lights;
    scene.add(fillLight);

    // 4 Floodlight Tower Lights
    const towerPositions: [number, number, number][] = [
      [55, 40, 55], [-55, 40, 55], [55, 40, -55], [-55, 40, -55]
    ];
    towerPositions.forEach((pos) => {
      const towerLight = new THREE.PointLight(0xffffff, 1.5, 120, 1.2);
      towerLight.position.set(...pos);
      towerLight.visible = preferences.lights;
      scene.add(towerLight);

      // Tower structure model
      const towerGeo = new THREE.CylinderGeometry(0.4, 0.8, 38, 8);
      const towerMat = new THREE.MeshStandardMaterial({ color: 0x1f2937, metalness: 0.8, roughness: 0.3 });
      const towerMesh = new THREE.Mesh(towerGeo, towerMat);
      towerMesh.position.set(pos[0], 19, pos[2]);
      scene.add(towerMesh);

      // Tower Light Head
      const headGeo = new THREE.BoxGeometry(4, 2, 2);
      const headMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const headMesh = new THREE.Mesh(headGeo, headMat);
      headMesh.position.set(pos[0], 38, pos[2]);
      headMesh.lookAt(0, 0, 0);
      scene.add(headMesh);
    });

    // 5. Cricket Field Oval
    const fieldGeo = new THREE.CylinderGeometry(48, 48, 0.2, 64);
    const fieldMat = new THREE.MeshStandardMaterial({
      color: 0x122e1b,
      roughness: 0.85,
      metalness: 0.1
    });
    const field = new THREE.Mesh(fieldGeo, fieldMat);
    field.position.y = -0.1;
    field.receiveShadow = true;
    scene.add(field);

    // Mowing pattern rings
    for (let r = 12; r <= 46; r += 8) {
      const ringGeo = new THREE.RingGeometry(r - 0.2, r + 0.2, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x184227,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = 0.01;
      scene.add(ring);
    }

    // Boundary Rope & Foam Wedges
    const boundaryRopeGeo = new THREE.TorusGeometry(44, 0.35, 12, 96);
    const boundaryMat = new THREE.MeshStandardMaterial({ color: 0x46664f, roughness: 0.4 });
    const boundaryRope = new THREE.Mesh(boundaryRopeGeo, boundaryMat);
    boundaryRope.rotation.x = Math.PI / 2;
    boundaryRope.position.y = 0.15;
    scene.add(boundaryRope);

    // 30-Yard Circle
    const innerCircleGeo = new THREE.RingGeometry(24.8, 25.2, 64);
    const innerCircleMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35
    });
    const innerCircle = new THREE.Mesh(innerCircleGeo, innerCircleMat);
    innerCircle.rotation.x = -Math.PI / 2;
    innerCircle.position.y = 0.02;
    scene.add(innerCircle);

    // 6. The 22-Yard Pitch Strip
    const pitchLength = 20.12; // 22 yards in meters
    const pitchWidth = 3.05;   // 10 feet in meters
    const pitchGeo = new THREE.BoxGeometry(pitchWidth, 0.1, pitchLength);
    const pitchMat = new THREE.MeshStandardMaterial({
      color: 0xc4a47c,
      roughness: 0.9,
      metalness: 0.05
    });
    const pitch = new THREE.Mesh(pitchGeo, pitchMat);
    pitch.position.y = 0.05;
    pitch.receiveShadow = true;
    scene.add(pitch);

    // Crease Lines (Bowling crease, popping crease, return creases at both ends)
    const creaseMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    [-8.8, 8.8].forEach((zPos) => {
      // Popping crease (1.22m in front of stumps)
      const popZ = zPos > 0 ? zPos - 1.22 : zPos + 1.22;
      const popGeo = new THREE.BoxGeometry(2.64, 0.02, 0.08);
      const popLine = new THREE.Mesh(popGeo, creaseMat);
      popLine.position.set(0, 0.11, popZ);
      scene.add(popLine);

      // Bowling crease (at the stumps)
      const bowlGeo = new THREE.BoxGeometry(2.64, 0.02, 0.05);
      const bowlLine = new THREE.Mesh(bowlGeo, creaseMat);
      bowlLine.position.set(0, 0.11, zPos);
      scene.add(bowlLine);

      // Return creases
      [-1.32, 1.32].forEach((xPos) => {
        const retGeo = new THREE.BoxGeometry(0.06, 0.02, 2.44);
        const retLine = new THREE.Mesh(retGeo, creaseMat);
        retLine.position.set(xPos, 0.11, zPos > 0 ? zPos - 1.22 : zPos + 1.22);
        scene.add(retLine);
      });

      // 3D Stumps & Bails (3 stumps per end)
      const stumpGeo = new THREE.CylinderGeometry(0.022, 0.022, 0.71, 12);
      const stumpMat = new THREE.MeshStandardMaterial({ color: 0xffe6a3, roughness: 0.3 });
      [-0.11, 0, 0.11].forEach((stumpX) => {
        const stump = new THREE.Mesh(stumpGeo, stumpMat);
        stump.position.set(stumpX, 0.45, zPos);
        stump.castShadow = true;
        scene.add(stump);
      });
      // Bail
      const bailGeo = new THREE.BoxGeometry(0.24, 0.02, 0.02);
      const bail = new THREE.Mesh(bailGeo, stumpMat);
      bail.position.set(0, 0.82, zPos);
      scene.add(bail);
    });

    // 7. Stadium Grandstand Terraces
    const standGeo = new THREE.CylinderGeometry(56, 50, 8, 48, 1, true);
    const standMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      side: THREE.BackSide,
      roughness: 0.7
    });
    const stand = new THREE.Mesh(standGeo, standMat);
    stand.position.y = 4;
    scene.add(stand);

    // Stadium Rim Glow Ring
    const rimGeo = new THREE.TorusGeometry(56, 0.4, 12, 64);
    const rimMat = new THREE.MeshBasicMaterial({ color: 0x46664f });
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.rotation.x = Math.PI / 2;
    rim.position.y = 8;
    scene.add(rim);

    // 8. Trajectories Group
    const trajGroup = new THREE.Group();
    scene.add(trajGroup);
    trajectoriesGroupRef.current = trajGroup;

    // 9. Heatmap Grid Group
    const heatGroup = new THREE.Group();
    scene.add(heatGroup);
    heatmapGroupRef.current = heatGroup;

    // Render loop
    let animationId: number;
    let clock = new THREE.Clock();

    let lastFrame = 0;
    const animate = (now = 0) => {
      animationId = requestAnimationFrame(animate);
      if(document.hidden || now - lastFrame < 1000 / preferences.fps) return;
      lastFrame = now;
      const delta = Math.min(clock.getDelta(), .1);

      // Smooth camera interpolation towards target
      if (cameraRef.current) {
        cameraRef.current.position.lerp(targetCameraPos.current, 0.06);
        currentLookAt.current.lerp(targetLookAt.current, 0.06);
        cameraRef.current.lookAt(currentLookAt.current);

        // Auto-rotate mode
        if (rotateRef.current && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
          const angle = delta * 0.2;
          const x = targetCameraPos.current.x;
          const z = targetCameraPos.current.z;
          targetCameraPos.current.x = x * Math.cos(angle) - z * Math.sin(angle);
          targetCameraPos.current.z = x * Math.sin(angle) + z * Math.cos(angle);
        }
      }

      renderer.render(scene, camera);
    };
    animate();

    // Mouse Controls (Orbit / Pan via drag)
    let isMouseDown = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const onMouseDown = (e: PointerEvent) => {
      container.setPointerCapture(e.pointerId);
      isMouseDown = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseMove = (e: PointerEvent) => {
      if (!isMouseDown) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;

      // Orbit camera around targetLookAt
      const pos = targetCameraPos.current;
      const look = targetLookAt.current;
      const radius = Math.sqrt((pos.x - look.x) ** 2 + (pos.z - look.z) ** 2);
      let theta = Math.atan2(pos.z - look.z, pos.x - look.x);
      theta -= deltaX * 0.01;

      pos.x = look.x + radius * Math.cos(theta);
      pos.z = look.z + radius * Math.sin(theta);
      pos.y = Math.max(2, Math.min(90, pos.y + deltaY * 0.15));
    };

    const onMouseUp = () => {
      isMouseDown = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY * 0.04;
      const dir = targetCameraPos.current.clone().sub(targetLookAt.current).normalize();
      const newPos = targetCameraPos.current.clone().addScaledVector(dir, zoomFactor);
      if (newPos.distanceTo(targetLookAt.current) > 8 && newPos.distanceTo(targetLookAt.current) < 130) {
        targetCameraPos.current.copy(newPos);
      }
    };

    container.addEventListener("pointerdown", onMouseDown);
    window.addEventListener("pointermove", onMouseMove);
    window.addEventListener("pointerup", onMouseUp);
    container.addEventListener("wheel", onWheel, { passive: false });

    container.style.touchAction = "none";
    const loseContext = (event: Event) => { event.preventDefault(); setContextLost(true); update({mode:"2D"}); };
    renderer.domElement.addEventListener("webglcontextlost", loseContext);
    container.addEventListener("pointercancel", onMouseUp);
    // Window Resize Handling
    const handleResize = () => {
      if (!containerRef.current || !renderer || !camera) return;
      const newW = Math.max(1,containerRef.current.clientWidth);
      const newH = Math.max(1,containerRef.current.clientHeight);
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(container);
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      container.removeEventListener("pointerdown", onMouseDown);
      window.removeEventListener("pointermove", onMouseMove);
      window.removeEventListener("pointerup", onMouseUp);
      container.removeEventListener("wheel", onWheel);
      window.removeEventListener("resize", handleResize);
      observer.disconnect();
      container.removeEventListener("pointercancel", onMouseUp);
      renderer.domElement.removeEventListener("webglcontextlost", loseContext);
      disposeObject(scene);
      renderer.dispose(); renderer.forceContextLoss();
      renderer.domElement.remove();
      sceneRef.current = null; rendererRef.current = null;
      trajectoriesGroupRef.current = null; heatmapGroupRef.current = null;
    };
  }, [preferences.quality, preferences.shadows, preferences.lights, preferences.fps]);

  useEffect(() => { if (heatmapGroupRef.current) heatmapGroupRef.current.visible = showHeatmap && showPitchGrid; }, [showHeatmap, showPitchGrid, preferences]);

  // Update Trajectories and Heatmap in the 3D scene when filter changes
  useEffect(() => {
    if (!trajectoriesGroupRef.current) return;
    const group = trajectoriesGroupRef.current;

    // Clear existing
    while (group.children.length > 0) {
      const child = group.children[0]; disposeObject(child); group.remove(child);
    }

    const filtered = BALL_TRAJECTORIES.filter((b) => {
      if (filterPhase !== "All" && b.phase !== filterPhase) return false;
      if (filterBowlerType === "Pace" && b.speed_kmh < 125) return false;
      if (filterBowlerType === "Spin" && b.speed_kmh >= 125) return false;
      return true;
    });

    filtered.forEach((ball) => {
      // Release point (bowler at z = -8.8m, release at height 2.1m)
      const releasePoint = new THREE.Vector3(-0.35, 2.15, -8.8);
      // Pitch impact point on pitch (z between -2.0m to +7.0m)
      const pitchZ = ball.length === "Yorker" ? 7.6 : ball.length === "Full" ? 5.8 : ball.length === "Good Length" ? 3.2 : -0.5;
      const impactPoint = new THREE.Vector3(ball.pitch_x, 0.12, pitchZ);
      // Post-bounce point towards stumps at z = 8.8m
      const stumpTarget = new THREE.Vector3(ball.pitch_x * 0.9, ball.bounce_height_m + 0.1, 8.8);

      // Trajectory 1: Pre-bounce arc
      const midPre = releasePoint.clone().lerp(impactPoint, 0.5);
      midPre.y = Math.max(releasePoint.y, impactPoint.y) + 0.35;
      const curve1 = new THREE.QuadraticBezierCurve3(releasePoint, midPre, impactPoint);

      // Trajectory 2: Post-bounce arc
      const midPost = impactPoint.clone().lerp(stumpTarget, 0.5);
      midPost.y = impactPoint.y + ball.bounce_height_m * 0.75;
      const curve2 = new THREE.QuadraticBezierCurve3(impactPoint, midPost, stumpTarget);

      // Color coding by length
      const lengthColors: Record<string, number> = {
        "Yorker": 0x46664f,      // Precision Cyan
        "Full": 0xa68a3b,        // Performance Lime
        "Good Length": 0xa7753c, // Tactical Amber
        "Short": 0xa14d3b        // Threat Red
      };
      const colorHex = lengthColors[ball.length] || 0x46664f;

      const points = [...curve1.getPoints(24), ...curve2.getPoints(20)];
      const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const lineMat = new THREE.LineBasicMaterial({
        color: colorHex,
        linewidth: 2,
        transparent: true,
        opacity: selectedTrajectory?.id === ball.id ? 1.0 : 0.65
      });
      const trajectoryLine = new THREE.Line(lineGeo, lineMat);
      trajectoryLine.userData.ball = ball;
      group.add(trajectoryLine);

      // Impact Spot Marker (Disc on pitch)
      const discGeo = new THREE.CircleGeometry(0.18, 16);
      const discMat = new THREE.MeshBasicMaterial({
        color: colorHex,
        side: THREE.DoubleSide
      });
      const disc = new THREE.Mesh(discGeo, discMat);
      disc.rotation.x = -Math.PI / 2;
      disc.position.copy(impactPoint);
      disc.position.y = 0.12;
      disc.userData.ball = ball;
      group.add(disc);

      // Wicket Star Marker if outcome was wicket
      if (ball.outcome === "Wicket") {
        const starGeo = new THREE.SphereGeometry(0.24, 12, 12);
        const starMat = new THREE.MeshBasicMaterial({ color: 0xa14d3b });
        const star = new THREE.Mesh(starGeo, starMat);
        star.position.copy(stumpTarget);
        group.add(star);
      }
    });
  }, [filterPhase, filterBowlerType, selectedTrajectory, preferences]);

  // Update Heatmap grid
  useEffect(() => {
    if (!heatmapGroupRef.current) return;
    const group = heatmapGroupRef.current;
    while (group.children.length > 0) {
      const child = group.children[0]; disposeObject(child); group.remove(child);
    }

    if (!showPitchGrid) return;

    // Pitch Zone Lines & Heatmap blocks
    const lengthZones = [
      { name: "Yorker (0-2m)", z1: 6.8, z2: 8.8, color: 0x46664f, opacity: 0.22 },
      { name: "Full (2-4m)", z1: 4.8, z2: 6.8, color: 0xa68a3b, opacity: 0.18 },
      { name: "Good Length (4-7m)", z1: 1.8, z2: 4.8, color: 0xa7753c, opacity: 0.25 },
      { name: "Short (>7m)", z1: -2.0, z2: 1.8, color: 0xa14d3b, opacity: 0.15 }
    ];

    lengthZones.forEach((z) => {
      const depth = Math.abs(z.z2 - z.z1);
      const centerZ = (z.z1 + z.z2) / 2;
      const zoneGeo = new THREE.PlaneGeometry(2.8, depth);
      const zoneMat = new THREE.MeshBasicMaterial({
        color: z.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: z.opacity
      });
      const zoneMesh = new THREE.Mesh(zoneGeo, zoneMat);
      zoneMesh.rotation.x = -Math.PI / 2;
      zoneMesh.position.set(0, 0.115, centerZ);
      group.add(zoneMesh);
    });
  }, [showPitchGrid, preferences]);

  return (
    <div className={`relative overflow-hidden rounded-xl border border-stone-300 bg-white ${className}`}>
      {/* 3D WebGL Canvas Container */}
      {contextLost && <p role="alert" className="absolute inset-0 bg-white z-50 p-4 text-stone-900">The graphics context was lost. Switch to 2D above to continue.</p>}
      <div ref={containerRef} role="application" aria-label="Sample 3D pitch. Arrow keys orbit; plus and minus zoom." tabIndex={0} className="w-full h-full cursor-grab active:cursor-grabbing" onKeyDown={event => {
        const p = targetCameraPos.current;
        if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","+","-","="].includes(event.key)) event.preventDefault();
        if(event.key === "ArrowLeft") p.x -= 3; if(event.key === "ArrowRight") p.x += 3;
        if(event.key === "ArrowUp") p.y = Math.min(90,p.y+3); if(event.key === "ArrowDown") p.y = Math.max(2,p.y-3);
        if(event.key === "+" || event.key === "=") p.multiplyScalar(.95); if(event.key === "-") p.multiplyScalar(1.05);
      }}/>
      <div className="absolute top-16 left-3 max-h-32 overflow-auto bg-slate-950/90 border border-white/10 rounded-lg text-slate-200 p-1.5 text-xs backdrop-blur-sm space-y-1">
        {BALL_TRAJECTORIES.filter(ball => filterPhase === "All" || ball.phase === filterPhase).filter(ball => filterBowlerType === "All" || (filterBowlerType === "Pace" ? ball.speed_kmh >= 125 : ball.speed_kmh < 125)).map(ball => (
          <button 
            key={ball.id} 
            aria-pressed={selectedTrajectory?.id === ball.id} 
            onClick={() => onSelectTrajectory?.(ball)}
            className={`block w-full text-left px-2 py-0.5 rounded text-[11px] font-mono transition-all ${
              selectedTrajectory?.id === ball.id ? "bg-emerald-600 text-white font-bold" : "text-slate-300 hover:bg-white/10"
            }`}
          >
            {ball.over}.{ball.ball} {ball.length} ({ball.speed_kmh} km/h)
          </button>
        ))}
      </div>

      {/* Top Floating Telemetry Overlay Bar */}
      <div className="absolute top-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto bg-slate-950/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 shadow-lg">
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] font-mono tracking-widest text-emerald-300 uppercase font-bold">
            3D VENUE SIMULATOR - CHINNASWAMY
          </span>
        </div>

        {/* Camera Preset Quick Switchers */}
        <div className="flex items-center gap-1 pointer-events-auto bg-slate-950/85 backdrop-blur-md p-1 rounded-lg border border-white/10 shadow-lg">
          {(
            [
              { id: "broadcast", label: "Broadcast", icon: Eye },
              { id: "top_down", label: "Top-Down", icon: Layers },
              { id: "bowler_view", label: "Bowler", icon: Crosshair },
              { id: "batter_view", label: "Batter", icon: Compass },
              { id: "pitch_heatmap", label: "Pitch Lab", icon: ShieldAlert },
              { id: "stadium_orbit", label: "360° Orbit", icon: RotateCcw }
            ] as const
          ).map((c) => {
            const Icon = c.icon;
            const isActive = currentCameraMode === c.id;
            return (
              <button
                key={c.id}
                onClick={() => handleCameraChange(c.id)}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-sans transition-all ${
                  isActive
                    ? "bg-emerald-600 text-white font-bold shadow"
                    : "text-slate-400 hover:text-white hover:bg-white/10"
                }`}
              >
                <Icon size={12} />
                <span className="hidden sm:inline">{c.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Length Clusters Legend Bottom Left */}
      <div className="absolute bottom-3 left-3 pointer-events-auto bg-slate-950/85 backdrop-blur-md p-3 rounded-xl border border-white/10 text-xs font-sans space-y-1.5 shadow-lg">
        <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-bold mb-1">
          Delivery Length Clusters
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span className="text-slate-300">Yorker (0-2m)</span>
          <span className="text-emerald-400 ml-auto font-mono font-bold">14%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
          <span className="text-slate-300">Full (2-4m)</span>
          <span className="text-cyan-400 ml-auto font-mono font-bold">24%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span className="text-slate-300">Good Length (4-7m)</span>
          <span className="text-amber-400 ml-auto font-mono font-bold">42%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
          <span className="text-slate-300">Short / Bouncer (&gt;7m)</span>
          <span className="text-rose-400 ml-auto font-mono font-bold">20%</span>
        </div>
      </div>

      <div className="absolute bottom-14 right-3 flex gap-2 bg-slate-950/85 backdrop-blur-md p-1.5 rounded-lg border border-white/10 text-slate-300 shadow-lg">
        <button aria-label="Zoom in" className="hover:text-emerald-400 p-1" onClick={() => { const offset=targetCameraPos.current.clone().sub(targetLookAt.current); if(offset.length()>9) targetCameraPos.current.copy(targetLookAt.current).add(offset.multiplyScalar(.9)); }}><ZoomIn size={18}/></button>
        <button aria-label="Zoom out" className="hover:text-emerald-400 p-1" onClick={() => { const offset=targetCameraPos.current.clone().sub(targetLookAt.current); if(offset.length()<115) targetCameraPos.current.copy(targetLookAt.current).add(offset.multiplyScalar(1.1)); }}><ZoomOut size={18}/></button>
      </div>
      {/* Floating Control Badges Bottom Right */}
      <div className="absolute bottom-3 right-3 flex items-center gap-2 pointer-events-auto">
        <button
          onClick={() => setShowPitchGrid(!showPitchGrid)}
          className={`px-3 py-1.5 rounded-lg border text-xs font-sans transition-all backdrop-blur-md ${
            showPitchGrid
              ? "bg-emerald-600 border-emerald-500 text-white font-bold shadow"
              : "bg-slate-950/85 border-white/10 text-slate-400 hover:text-white"
          }`}
        >
          {showPitchGrid ? "Pitch Grid ON" : "Pitch Grid OFF"}
        </button>
      </div>
    </div>
  );
};

