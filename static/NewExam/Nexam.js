
let BtnName = ""
$(document).ready(() => {
    $(".QsBtn.Active").attr("aria-label") == "1" ? $("#Previous, #Save_Previous").prop("disabled", true) : $("#Previous, #Save_Previous").prop("disabled", false);
    $("#SaveN, #SaveP").hide();
    $(".QsBtn").click((e) => {
        if ($(e.currentTarget).attr("aria-label") == "1") {
            $("#Previous").prop("disabled", true)
            $("#Save_Previous").hide()
            $("#SaveP").show()
        } else {
            $("#Previous").prop("disabled", false)
            $("#Save_Previous").prop("disabled", false).show()
            $("#SaveP").hide()
        };

        if ($(e.currentTarget).attr("aria-label") == $(".QsbtnSec .QsBtn").length) {
            $("#Next").prop("disabled", true)
            $("#Save_Next").hide()
            $("#SaveN").show()
        } else {
            $("#Next").prop("disabled", false)
            $("#Save_Next").show()
            $("#SaveN").hide()
        }

    })

    $("#Previous").click((e) => {
        BtnName = "Previous"
        $(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) - 1}]`).click()
    })

    $("#Save_Previous, #SaveP").click((e) => {
        BtnName = "Save"
        let QSscreen = $("#QsScreen")[0].contentDocument
        const QsType = $(QSscreen).find("[name=QsType]").val()
        const QSCode = $(QSscreen).find("[name=QSCode]").val()
        const QspCode = $("[name=QspCode]").val()
        if (QsType == "Subjective") {
            const Opval = $(QSscreen.forms[0]).find(".OptionRed:checked")
            const QSscreenVal = Opval.length > 0 ? Opval.val() : null;
            const data = {
                QspCode: QspCode,
                QSCode: QSCode,
                QSscreenVal: QSscreenVal
            }
            $.post('/exams/UpdateAns', data, (res) => {
                if (res.Update == "sucess") {
                    $(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) - 1}]`).click()
                }
            })
        } else {
            const Opval = $(QSscreen.forms[0]).find("#QnOptionsobj").text()
            const QSscreenVal = Opval.length > 0 ? Opval.val() : null;
            const data = {
                QspCode: QspCode,
                QSCode: QSCode,
                QSscreenVal: QSscreenVal
            }
            $.post(window.location.href, data, (res) => {
                debugger;
            })
        }

    })

    $("#Save_Next, #SaveN").click((e) => {
        BtnName = "Save"
        let QSscreen = $("#QsScreen")[0].contentDocument
        const QsType = $(QSscreen).find("[name=QsType]").val()
        const QSCode = $(QSscreen).find("[name=QSCode]").val()
        const QspCode = $("[name=QspCode]").val()
        if (QsType == "Subjective") {
            const Opval = $(QSscreen.forms[0]).find(".OptionRed:checked")
            const QSscreenVal = Opval.length > 0 ? Opval.val() : null;
            const data = {
                QspCode: QspCode,
                QSCode: QSCode,
                QSscreenVal: QSscreenVal
            }
            $.post('/exams/UpdateAns', data, (res) => {
                if (res.Update == "sucess") {
                    $(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) + 1}]`).click()
                }
            })
        } else {
            const Opval = $(QSscreen.forms[0]).find("#QnOptionsobj").text()
            const QSscreenVal = Opval.length > 0 ? Opval.val() : null;
            const data = {
                QspCode: QspCode,
                QSCode: QSCode,
                QSscreenVal: QSscreenVal
            }
            $.post(window.location.href, data, (res) => {
                debugger;
            })
        }
    })

    $("#Next").click((e) => {
        BtnName = "Next"
        $(`.QsBtn[aria-label = ${Number($(".QsBtn.Active").attr("aria-label")) + 1}]`).click()
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
            $("form").submit();
        }
    }, 1000)
}

function SetExTime(t) {
    $("#THourCount").text(t.getHours() < 10 ? `0${t.getHours()}` : t.getHours())
    $("#TMinCount").text(t.getMinutes() < 10 ? `0${t.getMinutes()}` : t.getMinutes())
    $("#TSecCount").text(t.getSeconds() < 10 ? `0${t.getSeconds()}` : t.getSeconds())
}

function RanderPage(o, pId) {
    let QSscreen = $("#QsScreen")[0].contentDocument

    if ($(QSscreen).find("[name=IsAnswered]").length > 0) {
        if ($(QSscreen).find("[name=IsAnswered]").val().length > 0 || BtnName == "Save") {
            $(".QsBtn.Active").removeClass("Not_Answered Active").addClass("Answered")
            $(o).removeClass("Not_Visited").addClass("Not_Answered Active")
        } else {
            $(".QsBtn.Active").removeClass("Active")
            $(o).removeClass("Not_Visited").addClass("Not_Answered Active")
        }
    }
    const QspCode = $("[name=QspCode]").val()
    $("#QsScreen").attr("src", `/exams/questions/${pId}?QspCode=${QspCode}`)

}



