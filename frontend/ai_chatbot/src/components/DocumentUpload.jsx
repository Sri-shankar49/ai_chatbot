import { useRef, useState } from "react";
import "./DocumentUpload.css";

const API_URL = "http://127.0.0.1:8000";
const MAX_FILE_SIZE = 5 * 1024 * 1024;

export default function DocumentUpload({ onUploaded }) {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function handleUpload(event) {
    event.preventDefault();

    if (!file || uploading) return;

    if (!["application/pdf", "text/plain"].includes(file.type)) {
      setError("Please select a PDF or TXT file.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("The file must be 5 MB or smaller.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setStatus("");
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Document upload failed."
        );
      }

      setStatus(
        data.message || "Document uploaded and processed successfully."
      );
      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      onUploaded?.(data);
    } catch (err) {
      setError(err.message || "Could not upload the document.");
      console.error("Document upload error:", err);
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="document-upload">
      <h2>Knowledge Base</h2>
      <p>Upload a PDF or text file to ask questions about it.</p>

      <form onSubmit={handleUpload}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null);
            setStatus("");
            setError("");
          }}
          disabled={uploading}
        />

        <button type="submit" disabled={!file || uploading}>
          {uploading ? "Uploading..." : "Upload document"}
        </button>
      </form>

      {file && (
        <p className="upload-file-name">
          Selected: {file.name}
        </p>
      )}

      {status && <p className="upload-success">{status}</p>}
      {error && <p className="upload-error">{error}</p>}
    </section>
  );
}