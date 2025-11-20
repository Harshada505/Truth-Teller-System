// App.js

import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from './Pages/Home';
import Login from './Pages/Login';
import Register from './Pages/Register';
import ProtectedRoute from './Components/ProtectedRoute';  // Assuming this is the ProtectedRoute component
import FileUpload from './Components/FileUpload';  // Assuming this is the ProtectedRoute component
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css"; // Import sToast style
function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/Register" element={<Register />} />
        {/* <Route path="/FileUpload" element={<ProtectedRoute element={FileUpload} />} /> */}
        <Route path="/FileUpload" element={<FileUpload />}/>

      </Routes>
        <ToastContainer />
    </BrowserRouter>
  );
}

export default App;
