function displayDiv(screen) {
    document.getElementById(screen).style.display = "block";
    if (screen == 'android') {
        document.getElementById('ios').style.display = "none";
        document.getElementById('web').style.display = "none";
    }
    if (screen == 'ios') {
        document.getElementById('android').style.display = "none";
        document.getElementById('web').style.display = "none";
    }
    if (screen == 'web') {
        document.getElementById('android').style.display = "none";
        document.getElementById('ios').style.display = "none";
    }
}

