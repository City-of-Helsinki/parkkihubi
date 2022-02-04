export function download(data: string, fileName: string): void {
    const blob: Blob = new Blob([data], { type: 'text/csv' });
    const blobURL: string = window.URL.createObjectURL(blob)

    const downloadLink: HTMLAnchorElement = document.createElement('a');
    downloadLink.style.display = 'none';
    downloadLink.href = blobURL;
    downloadLink.setAttribute('download', fileName);

    document.body.appendChild(downloadLink);
    downloadLink.click();
    setTimeout(function() {
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(blobURL);
    }, 200)
}
