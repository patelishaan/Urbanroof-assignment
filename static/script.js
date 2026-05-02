const inspectionInput = document.getElementById('inspection_file');
const thermalInput = document.getElementById('thermal_file');
const inspectionName = document.getElementById('inspection-name');
const thermalName = document.getElementById('thermal-name');

function handleFileSelect(input, displayEl) {
    input.addEventListener('change', (e) => {
        if(e.target.files.length > 0) {
            displayEl.textContent = e.target.files[0].name;
        }
    });
}

handleFileSelect(inspectionInput, inspectionName);
handleFileSelect(thermalInput, thermalName);

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('errorMsg');

    if(!inspectionInput.files[0] || !thermalInput.files[0]) {
        errorMsg.textContent = "Please upload both PDFs.";
        return;
    }

    const formData = new FormData();
    formData.append('inspection_report', inspectionInput.files[0]);
    formData.append('thermal_report', thermalInput.files[0]);

    // UI Loading state
    btn.disabled = true;
    btnText.textContent = "Processing AI (This may take a minute)...";
    loader.style.display = "block";
    errorMsg.textContent = "";

    try {
        const response = await fetch('/generate-report', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorText = "Something went wrong.";
            try {
                const data = await response.json();
                errorText = data.error || errorText;
            } catch (e) {
                // If the server returns an HTML page (like a 502 Bad Gateway or 413 Payload Too Large)
                errorText = `Server error (${response.status}). Please check your Render logs!`;
            }
            throw new Error(errorText);
        }

        // Handle file preview
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        const previewContainer = document.getElementById('previewContainer');
        const pdfIframe = document.getElementById('pdfIframe');
        const downloadBtn = document.getElementById('downloadBtn');
        const resetBtn = document.getElementById('resetBtn');
        const uploadForm = document.getElementById('uploadForm');

        // Show PDF in iframe
        pdfIframe.src = url;
        uploadForm.style.display = 'none';
        previewContainer.style.display = 'block';
        
        // Setup download button
        downloadBtn.onclick = () => {
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'Generated_Main_DDR.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };

        // Setup reset button
        resetBtn.onclick = () => {
            window.URL.revokeObjectURL(url);
            pdfIframe.src = '';
            previewContainer.style.display = 'none';
            uploadForm.style.display = 'block';
            uploadForm.reset();
            inspectionName.textContent = '';
            thermalName.textContent = '';
            btnText.textContent = "Generate DDR Report";
        };

    } catch (err) {
        errorMsg.textContent = err.message;
        btnText.textContent = "Generate DDR Report";
    } finally {
        btn.disabled = false;
        loader.style.display = "none";
    }
});
