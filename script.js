var main = document.querySelector("#main");
var crsr = document.querySelector(".cursor");

main.addEventListener("mousemove" , function(dets){
    crsr.style.left = dets.x + "px"
    crsr.style.top = dets.y + "px"
    
})


const form = document.querySelector("form"),
fileInput = document.querySelector(".file-input"),
progressArea = document.querySelector(".progress-area"),
uploadedArea = document.querySelector(".uploaded-area");

form.addEventListener("click", () =>{
  fileInput.click();
});

fileInput.onchange = ({target})=>{
  let file = target.files[0];
  if(file){
    let fileName = file.name;
    if(fileName.length >= 12){
      let splitName = fileName.split('.');
      fileName = splitName[0].substring(0, 13) + "... ." + splitName[1];
    }
    uploadFile(fileName);
  }
}

function uploadFile(name){
  let xhr = new XMLHttpRequest();
  xhr.open("POST", "php/upload.php");
  xhr.upload.addEventListener("progress", ({loaded, total}) =>{
    let fileLoaded = Math.floor((loaded / total) * 100);
    let fileTotal = Math.floor(total / 1000);
    let fileSize;
    (fileTotal < 1024) ? fileSize = fileTotal + " KB" : fileSize = (loaded / (1024*1024)).toFixed(2) + " MB";
    let progressHTML = `<li class="row">
                          <i class="fas fa-file-alt"></i>
                          <div class="content">
                            <div class="details">
                              <span class="name">${name} • Uploading</span>
                              <span class="percent">${fileLoaded}%</span>
                            </div>
                            <div class="progress-bar">
                              <div class="progress" style="width: ${fileLoaded}%"></div>
                            </div>
                          </div>
                        </li>`;
    uploadedArea.classList.add("onprogress");
    progressArea.innerHTML = progressHTML;
    if(loaded == total){
      progressArea.innerHTML = "";
      let uploadedHTML = `<li class="row">
                            <div class="content upload">
                              <i class="fas fa-file-alt"></i>
                              <div class="details">
                                <span class="name">${name} • Uploaded</span>
                                <span class="size">${fileSize}</span>
                              </div>
                            </div>
                            <i class="fas fa-check"></i>
                          </li>`;
      uploadedArea.classList.remove("onprogress");
      uploadedArea.insertAdjacentHTML("afterbegin", uploadedHTML);
    }
  });
  let data = new FormData(form);
  xhr.send(data);
}

class VoiceRecorder {
  constructor() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      console.log("Get user media suported");
    } else {
      console.log("Get user media not supported");

    }


    this.mediaRecorder
    this.stream
    this.chunks = []
    this.isRecording = false

    this.recorderRef = document.querySelector("#Recorder");
    this.playerRef = document.querySelector("#player");
    this.startRef = document.querySelector("#start");
    this.stopRef = document.querySelector("#stop");

    this.startRef.onclick = this.startRecording.bind(this);
    this.stopRef.onclick = this.stopRecording.bind(this);


    this.constraints = {
      audio: true,
      video: false
    }


  }

  //    handle sucees

  handleSucess(stream) {
    this.stream = stream
    this.stream.oninactive = () => {
      console.log("stream ended");
    }

    this.recorderRef.srcObject = this.stream
    this.mediaRecorder = new MediaRecorder(this.stream)
    this.mediaRecorder.ondataavailable = this.onMediaRecorderDataAvailable.bind(this);
    this.mediaRecorder.onstop = this.onMediaRecorderStop.bind(this);
    this.recorderRef.play();
    this.mediaRecorder.start();
  }

  onMediaRecorderDataAvailable(e) { this.chunks.push(e.data) }

  onMediaRecorderStop(e) {
    const blob = new Blob(this.chunks, { 'type': 'audio/ogg; codesc=opus' });
    const audioURL = window.URL.createObjectURL(blob)
    this.playerRef.src = audioURL;
    this.chunks = []
    this.stream.getAudioTracks().forEach(track => track.stop());
    this.stream = null
  }

  //   startRecording

  startRecording() {
    if(this.isRecording) return
    this.isRecording = true
    this.startRef.innerHTML="Recording....";
    this.playerRef.src='';
    navigator.mediaDevices.getUserMedia(this.constraints)
    .then(this.handleSucess.bind(this))
    .catch(this.handleSucess.bind(this))
  }

  //stopRecording

  stopRecording() {
    if(!this.isRecording) return
    this.isRecording = false
    this.startRef.innerHTML="Record";
    this.recorderRef.pause();
    this.mediaRecorder.stop()
  }

}

window.VoiceRecorder = new VoiceRecorder();