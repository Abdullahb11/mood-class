document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const resultContainer = document.getElementById("resultContainer");
  const previewImage = document.getElementById("previewImage");
  const emotionText = document.getElementById("emotionText");
  const loading = document.getElementById("loading");

  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop zone when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  // Handle dropped files
  dropZone.addEventListener("drop", handleDrop, false);
  fileInput.addEventListener("change", handleFileSelect, false);

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight(e) {
    dropZone.classList.add("highlight");
  }

  function unhighlight(e) {
    dropZone.classList.remove("highlight");
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  }

  function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
  }

  function handleFiles(files) {
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        uploadFile(file);
      } else {
        alert("Please upload an image file (PNG, JPG, or JPEG)");
      }
    }
  }

  function uploadFile(file) {
    const formData = new FormData();
    formData.append("image", file);

    // Show loading spinner
    loading.style.display = "flex";
    resultContainer.style.display = "none";

    fetch("/analyze", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Display the result
          previewImage.src = data.image_url;
          emotionText.textContent = data.emotion;
          resultContainer.style.display = "flex";
        } else {
          alert(data.error || "An error occurred while analyzing the image");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while uploading the image");
      })
      .finally(() => {
        loading.style.display = "none";
      });
  }
});
