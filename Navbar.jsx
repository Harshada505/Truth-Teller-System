import React, { useState } from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar position="static" style={{ background: "#6200ea", boxShadow: "0 4px 12px rgba(0,0,0,0.2)" }}>
      <Toolbar>
        {/* Logo or Brand */}
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600,fontSize: "2.1rem", textAlign: "center" }}>
          TruthTeller App
        </Typography>

        {/* Desktop Menu */}
        <Box sx={{ display: { xs: "none", sm: "flex" }, alignItems: "center", gap: 2 }}>
          <Button
            color="inherit"
            onClick={handleLogout}
            sx={{
              textTransform: "none",
              fontWeight: "bold",
              "&:hover": { backgroundColor: "rgba(255,255,255,0.1)" },
            }}
          >
            Logout
          </Button>

          {/* Profile Icon */}
          <Tooltip title="Account settings">
            <IconButton onClick={handleMenuOpen} size="small" sx={{ p: 0 }}>
              <Avatar alt="Profile" src="/broken-image.jpg" />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
            PaperProps={{
              elevation: 3,
              sx: {
                overflow: "visible",
                mt: 1.5,
                "& .MuiAvatar-root": {
                  width: 32,
                  height: 32,
                  ml: -0.5,
                  mr: 1,
                },
              },
            }}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
          >
            <MenuItem>
              <Avatar /> Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
