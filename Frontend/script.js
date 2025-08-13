// ===== Authentication =====
function login(){
  const email = document.getElementById('email').value;
  if(!email){
    alert("Please enter your email");
    return;
  }
  alert("Logged in as " + email);
  window.location.href = 'upload.html';
}

function signup(){
  alert("Signup clicked (add backend later)");
}

// ===== File Upload & Drag =====
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');

if(dropArea){
  dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('dragover');
  });

  dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('dragover');
  });

  dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('dragover');
    previewFile(e.dataTransfer.files[0]);
  });

  fileInput.addEventListener('change', () => {
    previewFile(fileInput.files[0]);
  });
}

function previewFile(file){
  if(file){
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      localStorage.setItem('soilImage', e.target.result);
    };
    reader.readAsDataURL(file);
  }
}

// ===== Fake Analysis =====
function analyzeSoil(){
  document.getElementById('analysis').innerText = "pH: 6.5 | Moisture: Medium | Organic Matter: High";
  document.getElementById('story').innerText = "Once upon a time, in your backyard, a patch of soil with pH 6.5 and medium moisture helped plants grow strong and healthy. Its high organic matter promised an abundant harvest for the season ahead.";
}
