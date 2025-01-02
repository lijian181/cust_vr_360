function getNetworkStatus() {
  return new Promise((resolve, reject) => {
    navigator.connection.addEventListener('change', () => {
      resolve(navigator.connection);
    });
  });
}
function calculateDownloadSpeed() {
    const testFileUrl = 'http://localhost:8080/net_speed'; //服务端预留的接口, 需要替换ip
    const startTime = Date.now();
    const xhr = new XMLHttpRequest();
    xhr.open('GET', testFileUrl, true);
    xhr.responseType = 'blob';
    xhr.onload = function () {
      if (xhr.status === 200) {
        const endTime = Date.now();
        const fileSizeInBytes = xhr.response.size;
        const downloadTimeInSeconds = (endTime - startTime) / 1000;
        const downloadSpeedInBps = fileSizeInBytes / downloadTimeInSeconds;
        const downloadSpeedInKbps = downloadSpeedInBps / 1024;
        //console.log("Estimated download speed (Kbps):", downloadSpeedInKbps);
        resolve(downloadSpeedInKbps);
    }
    };
    xhr.send();
  }
  

function getNetworkSpeedInUsingNavigator() {
    if ('connect' in navigator) {
        const connection = navigator.connection;
        // 下行速度，单位Mbps
        const downlink = connection.downlink;
        // effictiveType 2g'、'2g'、'3g'、'4g'
        const effectiveType = connection.effectiveType;
        console.log("effictive type", effectiveType);
        console.log("downlink Mbps", downlink);
        return {effectiveType, downlink}
    } else {
        // 获取失败就使用另外一套方法
        calculateDownloadSpeed().then(speed => {
            console.log("Estimated download speed (Kbps):", speed);
        }).catch(error => {
            console.error(error);
        });
    }   
}

