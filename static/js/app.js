document.addEventListener('DOMContentLoaded', () => {
    const researchForm = document.getElementById('researchForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingArea = document.getElementById('loadingArea');
    const statusText = document.getElementById('statusText');
    const resultArea = document.getElementById('resultArea');
    const downloadLink = document.getElementById('downloadLink');
    const errorArea = document.getElementById('errorArea');
    const errorText = document.getElementById('errorText');

    if (researchForm) {
        researchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const title = document.getElementById('productTitle').value;
            const description = document.getElementById('productDescription').value;

            // Reset UI
            errorArea.style.display = 'none';
            resultArea.style.display = 'none';
            loadingArea.style.display = 'block';
            submitBtn.disabled = true;
            statusText.textContent = "Agent is initializing...";

            const statuses = [
                "Searching the live web for competitors...",
                "Analyzing competitor features and pricing...",
                "Validating data to avoid hallucinations...",
                "Deep research on company histories...",
                "Synthesizing findings into a complete report...",
                "Generating final PDF report..."
            ];

            let statusIdx = 0;
            const statusInterval = setInterval(() => {
                if (statusIdx < statuses.length) {
                    statusText.textContent = statuses[statusIdx];
                    statusIdx++;
                }
            }, 10000); // Change status every 10 seconds

            try {
                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title, description }),
                });

                const data = await response.json();

                if (data.success) {
                    loadingArea.style.display = 'none';
                    resultArea.style.display = 'block';
                    downloadLink.href = data.pdf_url;
                } else {
                    throw new Error(data.error || "Failed to generate research.");
                }

            } catch (err) {
                loadingArea.style.display = 'none';
                errorArea.style.display = 'block';
                errorText.textContent = err.message;
            } finally {
                submitBtn.disabled = false;
                clearInterval(statusInterval);
            }
        });
    }

    // Scroll reveal/animation logic shared for landing
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
});
