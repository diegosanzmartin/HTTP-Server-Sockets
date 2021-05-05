function doSubmit(){
    // Form Data
    var formData = new FormData();

    var fileSelect = document.getElementById("data");
    if(fileSelect.files && fileSelect.files.length == 1){
        var file = fileSelect.files[0]
    }
    // Http Request  
    var request = new XMLHttpRequest();
    request.open('PUT', "/putfile");
    request.send(file);
}