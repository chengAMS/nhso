document.addEventListener("DOMContentLoaded", function () {
    const getStartedBtn = document.getElementById("get-started");
    if (getStartedBtn) {
        getStartedBtn.addEventListener("click", () => {
            alert("欢迎加入护理教育平台！在课程区域选择您感兴趣的内容开始学习。");
        });
    }
});
