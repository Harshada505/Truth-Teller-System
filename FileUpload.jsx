import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Navbar from './Navbar';

function FileUpload() {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [youtubeLink, setYoutubeLink] = useState("");
  const [language, setLanguage] = useState("en-IN"); // new state for language

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setVideoUrl(URL.createObjectURL(selectedFile));
    } else {
      setFile(null);
      setVideoUrl(null);
    }
  };

  const handleYouTubeLinkChange = (e) => {
    const link = e.target.value;
    setYoutubeLink(link);
    const videoId = link.split("v=")[1]?.split("&")[0] || link.split("/").pop();
    if (videoId) {
      setVideoUrl(`https://www.youtube.com/embed/${videoId}`);
    } else {
      setVideoUrl(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (file && youtubeLink) {
      toast.error("Please provide either a file or a YouTube link, not both.");
      setLoading(false);
      return;
    }

    if (youtubeLink) {
      try {
        const res = await fetch("http://127.0.0.1:5000/predict/link", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: youtubeLink, language }),
        });
        const result = await res.json();
        if (res.ok) {
          setResponse(result);
          toast.success("YouTube link processed successfully!");
        } else {
          toast.error(result.error || "Processing failed. Please try again.");
        }
      } catch (error) {
        toast.error("An error occurred. Please try again.");
      } finally {
        setLoading(false);
      }
    } else if (file) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("language", language);
      try {
        const res = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          body: formData,
        });
        const result = await res.json();
        if (res.ok) {
          setResponse(result);
          toast.success("File uploaded successfully!");
        } else {
          toast.error(result.error || "File upload failed. Please try again.");
        }
      } catch (error) {
        toast.error("An error occurred. Please try again.");
      } finally {
        setLoading(false);
      }
    } else {
      toast.error("Please provide either a file or a YouTube link.");
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="upload-background">
        <div className="container d-flex flex-column justify-content-center align-items-center mt-5">
          <div className="card p-4 shadow" style={{ width: "800px" }}>
            <h2 className="text-center mb-4">Upload File or Enter YouTube Link</h2>
            <form onSubmit={handleSubmit}>
              {/* Language selector */}
              <div className="mb-3">
                <label>Select Language</label>
                <select
                  className="form-control"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  <option value="en-IN">English</option>
                  <option value="hi-IN">Hindi</option>
                </select>
              </div>

              {/* File upload */}
              <div className="mb-3">
                <Box sx={{ maxWidth: "100%", padding: "20px", border: "1px solid gray" }}>
                  <input
                    className="form-control"
                    onChange={handleFileChange}
                    type="file"
                    accept="video/*"
                  />
                </Box>
              </div>

              <div className="text-center text-danger">OR</div>

              {/* YouTube link */}
              <div className="mb-3 mt-3 ">
                <input
                  className="form-control"
                  type="url"
                  placeholder="Enter YouTube video link"
                  value={youtubeLink}
                  onChange={handleYouTubeLinkChange}
                />
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
                  "Submit"
                )}
              </Button>
            </form>

            {/* Video preview */}
            {videoUrl && (
              <div className="mt-4">
                <h4>Video Preview</h4>
                {youtubeLink ? (
                  <iframe
                    width="100%"
                    height="315"
                    src={videoUrl}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                ) : (
                  <video controls width="100%" style={{ border: "1px solid black", marginTop: "10px" }}>
                    <source src={videoUrl} type={file?.type} />
                    Your browser does not support the video tag.
                  </video>
                )}
              </div>
            )}

            {/* Prediction summary */}
            {response && (
              <div className="response mt-4">
                <h4 className="text-center mb-3">Prediction Summary</h4>
                <Box display="flex" justifyContent="space-around" flexWrap="wrap" gap={2}>
                  {response.finalStatements.map((item, index) => (
                    <div key={index} className="card p-3" style={{ minWidth: "150px", textAlign: "center", flex: "1 1 30%" }}>
                      <h5>{item.label}</h5>
                      <p style={{ fontSize: "18px", fontWeight: "bold" }}>{item.percentage}%</p>
                    </div>
                  ))}
                </Box>
                <h5 className="mt-4">Predicted Statements</h5>
                {response.predicted_results.map((item, index) => (
                  <div key={index} className="card p-3 mt-2" style={{
                    borderLeft: `6px solid ${
                      item.predicted_label === "TRUE" ? "green" : item.predicted_label === "FALSE" ? "red" : "orange"
                    }`
                  }}>
                    <p style={{ margin: 0 }}>{item.original_text}</p>
                    <small className="text-muted">Label: {item.predicted_label}</small>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default FileUpload;
