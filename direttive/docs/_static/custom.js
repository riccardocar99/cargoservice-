/*
document.addEventListener("DOMContentLoaded", function() {
    var links = document.querySelectorAll('a.reference.external, a.reference.internal');
    for (var i = 0; i < links.length; i++) {
        if (links[i].getAttribute('href').includes('.pdf')) {
            links[i].setAttribute('target', 'viewPdf');
            links[i].setAttribute('rel', 'noopener noreferrer');
        }
    }
});
*/
document.addEventListener("DOMContentLoaded", function() {
    let pdfWindow = null; // Variabile per tenere traccia della finestra

    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (link && link.getAttribute('href') && link.getAttribute('href').includes('.pdf')) {
            e.preventDefault(); // Impediamo il comportamento di default
            
            const url = link.href;
            const targetName = "ViewPDF";

            // Se la finestra non esiste o è stata chiusa, la apriamo
            if (!pdfWindow || pdfWindow.closed) {
                pdfWindow = window.open(url, targetName);
            } else {
                // Se esiste già, cambiamo l'URL e portiamola in primo piano
                pdfWindow.location.href = url;
                pdfWindow.focus(); 
            }
        }
    }, true);
});