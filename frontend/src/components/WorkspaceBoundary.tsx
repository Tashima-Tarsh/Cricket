import React from "react";
export class WorkspaceBoundary extends React.Component<{children:React.ReactNode;workspace:string},{error:string|null}> {
  state: {error:string|null} = {error:null};
  static getDerivedStateFromError(error: Error) { return {error:error.message}; }
  componentDidUpdate(previous: {workspace:string}) { if(previous.workspace !== this.props.workspace && this.state.error) this.setState({error:null}); }
  render() { return this.state.error ? <section role="alert"><h1>Workspace could not be loaded</h1><p>Your browser could not open this workspace. Reload to request the latest files.</p><button onClick={() => window.location.reload()}>Reload application</button></section> : this.props.children; }
}
