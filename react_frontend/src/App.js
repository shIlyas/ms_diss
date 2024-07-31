import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './components/Home';
import HomeDefault from './components/HomeDefault'
import Management from './components/management/management'

const App = () => {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/home"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          >
            <Route index element={<HomeDefault />} />
            <Route path="manage" element={<Management />} />
          </Route>
          <Route path="/" element={<Navigate to="/home" />} />
        </Routes>

      </Router>
    </Provider>
  );
};

export default App;
