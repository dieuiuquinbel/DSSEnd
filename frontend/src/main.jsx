import React, { Component, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("React ErrorBoundary:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-slate-900">
          <div className="max-w-xl w-full bg-white rounded-3xl p-8 border border-slate-200 shadow-xl space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center text-xl font-black">
              ⚠️
            </div>
            <h2 className="text-base font-bold text-slate-900">Đã xảy ra lỗi khởi tạo giao diện</h2>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs font-mono text-rose-600 overflow-x-auto max-h-48">
              {String(this.state.error?.stack || this.state.error?.message || this.state.error)}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => {
                  localStorage.clear();
                  window.location.href = '/recommend';
                }}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 text-white cursor-pointer hover:bg-indigo-700 transition"
              >
                Xóa Cache & Tải lại trang
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 cursor-pointer hover:bg-slate-200 transition"
              >
                Tải lại bình thường
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)

