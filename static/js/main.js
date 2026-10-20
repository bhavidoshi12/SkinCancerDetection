// Skin Cancer Detection System — Main JavaScript Client Scripts

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navMenu = document.getElementById('navMenu');
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', function () {
      navMenu.classList.toggle('open');
      const expanded = navMenu.classList.contains('open');
      mobileToggle.setAttribute('aria-expanded', expanded);
    });
  }

  // 2. Alert Dismissal
  document.querySelectorAll('.alert-close').forEach(function (button) {
    button.addEventListener('click', function () {
      const alert = this.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // 3. Password Visibility Toggles
  document.querySelectorAll('.password-toggle-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          this.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
          `;
          this.setAttribute('aria-label', 'Hide password');
        } else {
          input.type = 'password';
          this.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          `;
          this.setAttribute('aria-label', 'Show password');
        }
      }
    });
  });

  // 4. Password Strength Guidance & Matching Validation
  const pwdInput = document.getElementById('reg_password');
  const confirmPwdInput = document.getElementById('reg_confirm_password');
  const pwdStrengthMsg = document.getElementById('password_strength_msg');
  const pwdMatchMsg = document.getElementById('password_match_msg');

  if (pwdInput && pwdStrengthMsg) {
    pwdInput.addEventListener('input', function () {
      const val = this.value;
      if (val.length === 0) {
        pwdStrengthMsg.textContent = 'Password must be at least 8 characters with at least one number.';
        pwdStrengthMsg.style.color = 'var(--color-text-muted)';
        return;
      }
      let strength = 0;
      if (val.length >= 8) strength++;
      if (/[0-9]/.test(val)) strength++;
      if (/[A-Z]/.test(val)) strength++;
      if (/[^A-Za-z0-9]/.test(val)) strength++;

      if (strength <= 1) {
        pwdStrengthMsg.textContent = 'Weak password: Add more characters and numbers.';
        pwdStrengthMsg.style.color = 'var(--color-danger)';
      } else if (strength === 2 || strength === 3) {
        pwdStrengthMsg.textContent = 'Moderate password strength.';
        pwdStrengthMsg.style.color = 'var(--color-warning)';
      } else {
        pwdStrengthMsg.textContent = 'Strong password.';
        pwdStrengthMsg.style.color = 'var(--color-success)';
      }

      if (confirmPwdInput && confirmPwdInput.value) {
        checkPasswordMatch();
      }
    });
  }

  function checkPasswordMatch() {
    if (!pwdInput || !confirmPwdInput || !pwdMatchMsg) return;
    if (confirmPwdInput.value.length === 0) {
      pwdMatchMsg.textContent = '';
      return;
    }
    if (pwdInput.value === confirmPwdInput.value) {
      pwdMatchMsg.textContent = 'Passwords match.';
      pwdMatchMsg.style.color = 'var(--color-success)';
    } else {
      pwdMatchMsg.textContent = 'Passwords do not match.';
      pwdMatchMsg.style.color = 'var(--color-danger)';
    }
  }

  if (confirmPwdInput) {
    confirmPwdInput.addEventListener('input', checkPasswordMatch);
  }

  // 5. Image Drag & Drop and Preview Interface
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('imageFileInput');
  const previewContainer = document.getElementById('previewContainer');
  const previewImage = document.getElementById('previewImage');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const fileSizeDisplay = document.getElementById('fileSizeDisplay');
  const removeImageBtn = document.getElementById('removeImageBtn');
  const uploadForm = document.getElementById('uploadForm');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const analyzeBtnText = document.getElementById('analyzeBtnText');
  const analyzeSpinner = document.getElementById('analyzeSpinner');
  const uploadError = document.getElementById('uploadError');

  if (dropzone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        handleFileSelection(files[0]);
      }
    });

    dropzone.addEventListener('click', (e) => {
      if (e.target !== removeImageBtn && !removeImageBtn?.contains(e.target)) {
        fileInput.click();
      }
    });

    fileInput.addEventListener('change', function () {
      if (this.files.length > 0) {
        handleFileSelection(this.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    if (!file) return;

    // Reset error
    if (uploadError) {
      uploadError.style.display = 'none';
      uploadError.textContent = '';
    }

    const validExtensions = ['image/jpeg', 'image/png', 'image/jpg'];
    const maxSizeBytes = 10 * 1024 * 1024; // 10MB

    // Check extension / MIME type
    if (!validExtensions.includes(file.type) && !/\.(jpe?g|png)$/i.test(file.name)) {
      showUploadError(`Invalid file format "${file.name}". Please upload a JPG, JPEG, or PNG image.`);
      resetUpload();
      return;
    }

    // Check file size
    if (file.size > maxSizeBytes) {
      showUploadError(`File size exceeds 10MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB).`);
      resetUpload();
      return;
    }

    // Read and preview image
    const reader = new FileReader();
    reader.onload = function (e) {
      if (previewImage) {
        previewImage.src = e.target.result;
      }
      if (previewContainer) {
        previewContainer.style.display = 'block';
      }
      if (fileNameDisplay) {
        fileNameDisplay.textContent = file.name;
      }
      if (fileSizeDisplay) {
        fileSizeDisplay.textContent = `${(file.size / 1024).toFixed(1)} KB`;
      }
      if (analyzeBtn) {
        analyzeBtn.disabled = false;
      }
    };
    reader.onerror = function () {
      showUploadError("Could not read the selected file. Please select another image.");
      resetUpload();
    };
    reader.readAsDataURL(file);
  }

  function showUploadError(msg) {
    if (uploadError) {
      uploadError.textContent = msg;
      uploadError.style.display = 'block';
    } else {
      alert(msg);
    }
  }

  function resetUpload() {
    if (fileInput) fileInput.value = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (previewImage) previewImage.src = '';
    if (analyzeBtn) analyzeBtn.disabled = true;
  }

  if (removeImageBtn) {
    removeImageBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      resetUpload();
    });
  }

  if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
      if (fileInput && fileInput.files.length === 0) {
        e.preventDefault();
        showUploadError("Please select an image file before clicking Analyze.");
        return;
      }
      if (analyzeBtn) {
        analyzeBtn.disabled = true;
      }
      if (analyzeBtnText) {
        analyzeBtnText.textContent = "Processing lesion imagery...";
      }
      if (analyzeSpinner) {
        analyzeSpinner.style.display = 'inline-block';
      }
    });
  }

  // 6. Test Cases Management & Persistence
  const testCasesForm = document.getElementById('testCasesForm');
  const saveNotice = document.getElementById('tcSaveNotice');

  // Dynamic styling for status selects
  document.querySelectorAll('.tc-status-select').forEach(function (select) {
    function updateSelectStyle() {
      select.classList.remove('not-run', 'pass', 'fail');
      if (select.value === 'Pass') {
        select.classList.add('pass');
      } else if (select.value === 'Fail') {
        select.classList.add('fail');
      } else {
        select.classList.add('not-run');
      }
    }
    updateSelectStyle();
    select.addEventListener('change', function () {
      updateSelectStyle();
      updateKpis();
    });
  });

  function updateKpis() {
    const selects = document.querySelectorAll('.tc-status-select');
    let passed = 0;
    let failed = 0;
    let notRun = 0;
    selects.forEach(s => {
      if (s.value === 'Pass') passed++;
      else if (s.value === 'Fail') failed++;
      else notRun++;
    });

    const passedEl = document.getElementById('kpiPassed');
    const failedEl = document.getElementById('kpiFailed');
    const notRunEl = document.getElementById('kpiNotRun');

    if (passedEl) passedEl.textContent = passed;
    if (failedEl) failedEl.textContent = failed;
    if (notRunEl) notRunEl.textContent = notRun;
  }

  if (testCasesForm) {
    testCasesForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(testCasesForm);

      const saveBtn = document.getElementById('saveTcBtn');
      const originalText = saveBtn ? saveBtn.innerHTML : 'Save';
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = `Saving...`;
      }

      fetch(testCasesForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (saveNotice) {
          saveNotice.textContent = 'All test case execution results saved persistently to SQLite database.';
          saveNotice.className = 'alert alert-success';
          saveNotice.style.display = 'block';
          setTimeout(() => {
            saveNotice.style.display = 'none';
          }, 4000);
        }
      })
      .catch(err => {
        // Fallback standard submit
        testCasesForm.submit();
      })
      .finally(() => {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = originalText;
        }
      });
    });
  }
});
