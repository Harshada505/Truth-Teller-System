import React, { useState } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import { Link, useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { toast } from "react-toastify"; 
import { API_BASE_URL } from "../const.js";

import 'react-toastify/dist/ReactToastify.css';

function Login() {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate(); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const form = e.target;
    const formData = new FormData(form);

    const data = {
      username: formData.get("username"), // Corrected the typo here
      password: formData.get("password"),
    };
    console.log(data);
   
    try {
      const response = await fetch(API_BASE_URL + "login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
  // console.log(result.access_token);
  
      if (response.ok) {
        toast.success("Login successful!");
        localStorage.setItem("token", result.access_token);

        navigate("/FileUpload");
      } else {
        toast.error(result.message || "Login failed. Please try again.");
      }
    } catch (error) {
      toast.error("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-background">
      <div className="container d-flex flex-column justify-content-center align-items-center vh-100">
        <h1 className="text-center mb-4">TruthTeller App</h1>
        <div className="card p-4 shadow" style={{ width: "400px" }}>
          <h2 className="text-center mb-4">Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <Box sx={{ maxWidth: "100%" }}>
                <TextField
                  fullWidth
                  label="Username" // Updated label to "Username"
                  id="username"
                  name="username"
                  type="text"
                  required
                />
              </Box>
            </div>

            <div className="mb-3">
              <Box sx={{ maxWidth: "100%" }}>
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={() => setShowPassword((prev) => !prev)}
                          onMouseDown={(e) => e.preventDefault()}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </div>

            <Button
              type="submit"
              className="w-100"
              variant="contained"
              style={{ background: "green", color: "white" }}
              disabled={loading}
            >
              {loading ? (
                <CircularProgress size={24} style={{ color: "white" }} />
              ) : (
                "Login"
              )}
            </Button>
          </form>

          <div className="mt-3 text-center">
            Don't have an account?{" "}
            <Link to="/Register" style={{ textDecoration: "none" }}>
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
