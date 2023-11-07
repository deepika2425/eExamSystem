

$('#myModal').on('shown.bs.modal', function (obj) {
    debugger;
    $('#myInput').trigger('focus')
  })


  function UpdateModal(Upjson,PageUrl){
    Upjson = Upjson.split(",");
    let UpSearch = "";
    $(Upjson).each((UjIndex,UjObj)=>{
        let UpUrlSp = UjObj.split(":")
        Upjson.length - 1 == UjIndex ? UpSearch += `${UpUrlSp[0]}=${UpUrlSp[1]}` : UpSearch += `${UpUrlSp[0]}=${UpUrlSp[1]}&`
    })
    let Ifrem = $('#UpdateModal .modal-body #Update_Ifrem')[0];
        Ifrem.src = `${PageUrl}?${UpSearch}`
    $('#UpdateModal').modal({
        backdrop: 'static',
        keyboard : false
    })
    $("#UpdateSaveBtn").click((UpBtnObj)=>{
        $($($(UpBtnObj.currentTarget).closest(".modal-content").find("iframe"))[0].contentDocument).find("form").submit()
        $('#UpdateModal').modal("hide")
        $("form").submit();
    })
    $("#UpdateCloseBtn").click((ClBtnObj)=>{
        $($(ClBtnObj.currentTarget).closest(".modal-content").find("iframe")).removeAttr("src")
    })
  }
  async function ConfirmDelet(){
    let DeletePromise = new Promise(function (DeleteResolve, DeleteReject) {
      $('#DeleteModal').modal({backdrop: 'static', keyboard : false })
      $("#DeleteModal #delete_input_field").keyup((object) => {
        object.target.value == "Delete" ? $("#DeleteModal #confirm_delete").removeAttr("disabled") : $("#DeleteModal #confirm_delete").attr("disabled", "disabled");
      });
      $("#DeleteModal #confirm_delete").click(()=>{
        $("#DeleteModal #delete_input_field").val() == "Delete" ? DeleteResolve(true) : DeleteResolve(false);
      });
      $("#DeleteModal #close_delete,#DeleteModal .close").click(() => {
        $("#DeleteModal #confirm_delete").attr("disabled", "disabled");
        DeleteReject(false);
        $("#DeleteModal #delete_input_field").val("");
      });
    })
    return await DeletePromise.then(
      function (value) { return value },
      function (error) { return error }
    )
  }
  async function DeleteModal(dt){
    if (await ConfirmDelet()){
      $.post(`?mode=delete&data=${dt}`,(result)=>{
        $("form").submit();
      });
    }
  };

  function StartExam(){
    let NewExam = window.open('StartExam.html','NewExam',`width=${window.outerWidth},height=${window.outerHeight},scrollbars=yes,top="0", left="0"`)
    NewExam.document.write('Start Test')
  };