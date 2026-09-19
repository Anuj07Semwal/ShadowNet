import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { failed: boolean };

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  componentDidCatch(error: Error, details: ErrorInfo) {
    console.error("ShadowNet interface error", error, details);
  }

  render() {
    if (this.state.failed) {
      return (
        <main className="startup-error" role="alert">
          <div>
            <p>SHADOWNET SYSTEM NOTICE</p>
            <h1>The investigation workspace could not start</h1>
            <span>Refresh the page once. If the problem continues, check the browser console and restart the frontend terminal.</span>
            <button type="button" onClick={() => window.location.reload()}>Reload workspace</button>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}
