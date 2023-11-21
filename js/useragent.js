async function getBrowserType() {
    try {
        let userAgent = navigator.userAgent;
        console.log(userAgent);
        let browserType = "Unknown";

        if  (userAgent.includes("Edg/")) {
            browserType = "Microsoft Edge";
        }
        else if (userAgent.includes("Chrome") && !userAgent.includes("Edg/")) {
            browserType = "Google Chrome";
        }
        else if (userAgent.includes("Firefox")) {
            browserType = "Mozilla Firefox";
        }
        else if (userAgent.includes("Safari") && !userAgent.includes("Chrome") && !userAgent.includes("Edg/")) {
            browserType = "Apple Safari";
        }
        else if (userAgent.includes("OPR") || userAgent.includes("Opera")) {
            browserType = "Opera";
        }
        else if (userAgent.includes("Trident")) {
            browserType = "Microsoft Internet Explorer";
        }
        else if (userAgent.includes("MSIE")) {
            browserType = "Microsoft Internet Explorer";
        }
        else if ((window.navigator.brave && window.navigator.brave.isBrave && await window.navigator.brave.isBrave()) || userAgent.includes('Brave')) {
            browserType = "Brave";
        }
        return browserType;
    } catch (error) {
        console.error("An error occurred in getBrowserType:", error);
        return "Unknown";
    }
}


window.onload = async () => {
    let browserType = await getBrowserType();
    let errorMessage = '';

    switch(browserType) {
        case "Google Chrome":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/chrome.png" class="my-icon" alt="Chrome Icon">
            <span class="title-class-Google-Chrome">Google Chrome Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            It looks like you're using an older version of Google Chrome that we no longer support.
            To continue to enjoy a safer, faster, and better browsing experience,
            please update to the latest version of Google Chrome.
        </div>`;
            break;
        case "Mozilla Firefox":
            errorMessage = `
           <div class="title-bar">
               <img src="/images/firfox.jpg" class="my-icon" alt="Firefox Icon">
               <span class="title-class-Mozilla-Firefox ">Firefox Update Required</span>
                <button class="my-custom-close" onclick="Swal.close()">&times;</button>
            </div>
            <div class="my-error-message">
                It looks like you're using an older version of Firefox that we no longer support.
                To continue to enjoy a safer, faster, and better browsing experience,
                please update to the latest version of Firefox.
            </div>`;
                    break;
        case "Apple Safari":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/applesafari.png" class="my-icon" alt="Apple Safari Icon">
            <span class="title-class-Apple-Safari">Safari Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            This is a custom message for Apple Safari. Please update to the latest version for the best experience.
        </div>`;
            break;
        case "Opera":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/oplogoimage-removebg-preview.png" class="my-icon" alt="Opera Icon">
            <span class="title-class-Opera">Opera Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            This is a custom message for Opera. Update your browser to stay secure and enjoy new features.
        </div>`;
            break;
        case "Microsoft Internet Explorer":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/inter.png" class="my-icon" alt="Internet Explorer Icon">
            <span class="title-class-Microsoft-Internet-Explorer">Internet Explorer Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            Internet Explorer is outdated. For improved security and performance, please switch to a modern browser.
        </div>`;
            break;
        case "Microsoft Edge":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/microedge.png" class="my-icon" alt="edge icon">
           <span style="display: block; text-align: center; position: absolute; left: 40%; transform: translate(-50%); margin: 20px 0; font-size: 22px; font-family: 'Arial', sans-serif;">Microsoft Edge Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            Stay fast and secure. Update Microsoft Edge to the latest version.
        </div>`;
            break;
        case "Brave":
            errorMessage = `
        <div class="title-bar">
            <img src="../images/brave.jpg" class="my-icon" alt="Brave Icon">
            <span class="title-brave">Brave Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            Brave browser update available. Upgrade now to ensure privacy and security.
        </div>`;
            break;
        default:
            errorMessage = `
        <div class="title-bar">
            <i class="fas fa-question-circle my-icon"></i>
            <span class="my-title-class">Browser Update Required</span>
            <button class="my-custom-close" onclick="Swal.close()">&times;</button>
        </div>
        <div class="my-error-message">
            Your browser is not recognized. For optimal performance and security, please update your browser.
        </div>`;
            break;

    }

    Swal.fire({
        html: errorMessage,
        confirmButtonText: 'Update',
        width: '600px',
        heightAuto: false,
        grow: false,
        customClass: {
            confirmButton: 'my-confirm-button',
            popup: 'my-popup-class',
            title: 'my-title-class'
        },
        showCloseButton: false,
        buttonsStyling: false,
        allowOutsideClick: false,
        allowEscapeKey: false
    });

}
