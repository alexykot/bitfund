for(var i = 0; i < 8; i++) { var scriptId = 'u' + i; window[scriptId] = document.getElementById(scriptId); }

$axure.eventManager.pageLoad(
function (e) {

});

$axure.eventManager.focus('u4', function(e) {

if ((GetWidgetText('u3')) == ('')) {

SetWidgetFormText('u3', GetWidgetText('u4'));

SetWidgetFormText('u4', '');

}
});

$axure.eventManager.blur('u4', function(e) {

if ((GetWidgetText('u4')) == ('')) {

SetWidgetFormText('u4', GetWidgetText('u3'));

SetWidgetFormText('u3', '');

}
});

$axure.eventManager.focus('u7', function(e) {

if ((GetWidgetText('u6')) == ('')) {

SetWidgetFormText('u6', GetWidgetText('u7'));

SetWidgetFormText('u7', '');

}
});

$axure.eventManager.blur('u7', function(e) {

if ((GetWidgetText('u7')) == ('')) {

SetWidgetFormText('u7', GetWidgetText('u6'));

SetWidgetFormText('u6', '');

}
});
gv_vAlignTable['u1'] = 'center';