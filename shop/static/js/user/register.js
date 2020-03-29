$(function () {
    let $username = $('#user_name');  //获取用户名标签
    let $mobile = $("#tel"); //获取手机号
    let $smsCodeBtn = $(".sms-captcha");  //发送短信验证按钮
    let $register = $(".form-contain");       //form表单所有元素  不能获取到submit按钮那里去




    //鼠标移出用户名输入框时执行判断
    $username.blur(function () {
        fn_check_username();
    });

    // 用户名是否存在
    function fn_check_username() {
        let sUsername = $username.val(); //获取表单数据
        let sReturnValue = '';
        // 前端校验不
        if (sUsername === "") {
            message.showError('用户名能为空！');
            return
        } else if (!(/\w{5,20}/).test(sUsername)) {
            message.showError('请输入5~20位字符的用户名！');
            return
        }

        //ajax请求判断数据库是否存在  后端校验
        $.ajax({
            url: '/user/username/' + sUsername + '/',
            type: 'GET',
            dataType: 'json',
            async: false,
        })

            .done(function(arg){
                if (arg.data.count !== 0) {  // 不等于0表示已经注册了
                    message.showError("用户名已被注册，请重新输入");
                    sReturnValue = "";
                } else {
                    sReturnValue = "success";
                    message.showSuccess("用户名可以正常使用")
                }
            })
            .fail(function(){
                message.showError("服务器超时，请重试！");
                sReturnValue = "";
            });



        return sReturnValue  //返回出该信息
    }

    //鼠标移出手机号输入框时执行判断
    $mobile.blur(function () {
        fn_check_mobile();
    });

    // 手机号是否存在
    function fn_check_mobile() {
        let sMobile = $mobile.val();
        let sReturnMobileValue = "";
        // 前端校验
        if (sMobile === "") {
            message.showError("手机号为空");

        } else if (!(/^1[3-9]\d{9}/).test(sMobile)) {
            message.showError("请输入正确的手机号格式");

        }
        //ajax请求判断数据库是否存在  后端校验
        $.ajax({
            url: "/user/mobile/" + sMobile + '/',
            type: "GET",
            dataType: "json",
            async: false,  // 关闭异步
            })

            .done(function (arg) {
                if (arg.data.count !== 0) {
                    message.showError(sMobile + "手机号已被注册，请重新输入");
                    sReturnMobileValue = "";
                } else {
                    message.showSuccess(sMobile + "手机号能正常使用");
                    sReturnMobileValue = "success";
                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试！");
                sReturnMobileValue = "";
            });

        return sReturnMobileValue  //返回出该信息
    }

    //短信验证
    $smsCodeBtn.click(function () {
        // 判定用户名是否为空是否有输入
        if (fn_check_username() !== "success") {
            message.showError("用户名不正确");
            return
        }

        // 判定手机号是否有输入
        if (fn_check_mobile() !== "success") {
            message.showError("手机号不正确");
            return
        }


        let dataParams = {
            'mobile': $mobile.val(),

        };
        $.ajax({
            url: "/user/sms_code/",
            type: "POST",
            data: JSON.stringify(dataParams),
            success: function (arg) {
                console.log(arg);
                if (arg.errno === "0") {   // errno: "0", errmsg: "短信发送正常", data: null
                    message.showError("短信验证码发送成功");
                    //倒计时功能
                    let num = 60;
                    // 设置计时器
                    let t = setInterval(function () {
                        if (num === 1) {
                            clearInterval(t);
                            $smsCodeBtn.html("重新发送验证码")
                        } else {
                            num -= 1;
                            //展示倒计时信息
                            $smsCodeBtn.html(num + "秒");
                        }

                    }, 1000)
                } else {
                    message.showError(arg.errmsg);
                }
            },
            error: function () {
                message.showError("服务器超时，请重试")
            }
        })
    });


    //注册
    $register.submit(function (res) {
        //阻止默认提交操作
        res.preventDefault();

        //获取用户输入的内容
        let sUsername = $username.val(); // 用户输入的用户名
        let sPassword = $("input[name=pwd]").val();  //用户输入的密码
        let sMobile = $mobile.val();   //用户输入的手机号码
        let sSmsCode = $("input[name=sms_captcha]").val();   //短信验证码
        let sAllow = $('input[name=allow]:checked').val();  //隐私条例选择


        //判断用户名是否已被注册
        if (fn_check_username() !== "success") {
            //alert("用户已被注册，请重新输入");
            return
        }
        //判断手机号是否已被注册
        if (fn_check_mobile() !== "success") {
            return
        }


        //判断密码长度是否合适
        if (sPassword.length < 5 || sPassword.length > 18)   {
            message.showError("密码长度不在6-20范围内");
            return
        }


        //判断短信验证码输入位数是否为6位
        if (!(/^\d{6}$/).test(sSmsCode)) {
            message.showError("短信验证码长度不正确");
            return
        }

        // 判断隐私条例是否勾选
        if(sAllow !== "on"){
            message.showError("请勾选隐私条例！");
            return
        }

        //发起注册
        //1.注册参数
        let sDataParams = {
            "username": sUsername,
            'mobile': sMobile,
            'password': sPassword,
            'sms_text': sSmsCode,
        };
        //创建ajax请求
        $.ajax({
            url: "/user/register/",  //请求地址
            type: "POST",            //请求类型
            data: JSON.stringify(sDataParams),  //请求参数
            contentType: "application/json;charset=utf-8", //请求数据类型前端发送给后端的
            dataType: "json",   //后端返回给前端的数据类型
            success: function (arg) {
                if (arg.errno === "0") {
                    message.showSuccess("恭喜注册成功");
                    //这里需要改进后台管理时
                    setTimeout(function () {
                        window.location.href = "/user/login/";  //注册成功后跳转到登录界面  document.referrer  回到上一个页面
                    }, 1500);
                } else {
                    message.showError("注册失败：" + arg.errmsg)
                }
            },
            error: function () {
                message.showError("服务器超时，请重试")
            }
        })

    });

});



