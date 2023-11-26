
// window.onbeforeunload = function(){
//     return 'Are you sure you want to leave?';
//   };

//   window.onunload = function() {
//     alert('Bye.');
// }

// window.onbeforeunload = function() {
//     if (isDirty) {
//       return 'There is unsaved data.';
//     }
//     return undefined;
//   }

function goodbye(e) {
    if (!e) e = window.event;
    //e.cancelBubble is supported by IE - this will kill the bubbling process.
    e.cancelBubble = true;
    e.returnValue = 'You sure you want to leave?'; //This is displayed on the dialog

    //e.stopPropagation works in Firefox.
    if (e.stopPropagation) {
        e.stopPropagation();
        e.preventDefault();
    }
    $.get("/endexam");
}
window.onbeforeunload = goodbye;

$(document).ready(() => {
    $(".QsBtn.Active").attr("aria-label") == "1" ? $("#Previous, #Save_Previous").prop("disabled", true) : $("#Previous, #Save_Previous").prop("disabled", false);

    $(".QsBtn").click((e) => {
        $(e.currentTarget).attr("aria-label") == "1" ?
            $("#Previous, #Save_Previous").prop("disabled", true) : $("#Previous, #Save_Previous").prop("disabled", false);
        $(e.currentTarget).attr("aria-label") == $(".QsbtnSec .QsBtn").length ?
            $("#Next, #Save_Next").prop("disabled", true) : $("#Next, #Save_Next").prop("disabled", false);
        $(".QsBtn.Active").removeClass("Active")
        $(e.currentTarget).removeClass("Not_Visited").addClass("Not_Answered Active")
    })

    $("#Previous").click((e) => {
        `${$(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) - 1}]`).click()}`
    })

    $("#Save_Previous").click((e) => {
        `${$(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) - 1}]`).click()}`
    })

    $("#Submit").click((e) => {

    })

    $("#Save_Next").click((e) => {
        `${$(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) + 1}]`).click()}`
    })

    $("#Next").click((e) => {
        `${$(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) + 1}]`).click()}`
    })
})

function TimeLeft(H, M, S) {
    let nd = new Date();
    nd.setHours(H)
    nd.setMinutes(M)
    nd.setSeconds(S)
    SetExTime(nd);
    let Tl = setInterval(() => {
        nd = new Date(nd.getTime() - 1000)
        SetExTime(nd);
        if (nd.getHours() == 0o0 && nd.getMinutes() == 0o0 && nd.getSeconds() == 0o0) {
            clearInterval(Tl)
            alert("Times Up !!!!")
        }
    }, 1000)
}

function SetExTime(t) {
    $("#THourCount").text(t.getHours() < 10 ? `0${t.getHours()}` : t.getHours())
    $("#TMinCount").text(t.getMinutes() < 10 ? `0${t.getMinutes()}` : t.getMinutes())
    $("#TSecCount").text(t.getSeconds() < 10 ? `0${t.getSeconds()}` : t.getSeconds())
}

function RanderPage(pId) {
    $("#QsScreen").attr("src", `/exams/questions/${pId}`)
}

