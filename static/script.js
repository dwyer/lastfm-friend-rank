function getUserURL(user) {
  return 'http://www.last.fm/user/' + user;
}

function getUserLink(user) {
  return '<a href="'+getUserURL(user)+'" target="_blank">'+user+'</a>'
}

$(document).ready(function() {
  var $username = $('#username');
  $username.focus();
  $('#the-form').submit(function() {
    var $progress = $('#progress');
    var $status = $('#status-bar');
    var $list = $('#friend-list');
    var user = $username.val();
    var url = '/friends?user=' + user;
    $username.val('');
    $progress.attr('value', 0).attr('max', 0);
    $status.empty();
    $list.empty();
    $.ajax({
      url: url,
      success: function(data) {
        var friends = $.parseJSON(data);
        var count = 0;
        $progress.attr('max', friends.length);
        $status.append('Processed <span id="friend-number">0</span> of '+
            friends.length+' friends for '+getUserLink(user));
        $(friends).each(function(i, friend) {
          $.ajax({
            url: '/compare?user='+user+'&friend='+friend,
            success: function (data) {
              var appended = false;
              var score = $.parseJSON(data);
              var $item = $('<li>'+getUserLink(friend)+
                  ' <span class="score">'+score+'</span></li>');
              $('#friend-number').empty().append(++count);
              $progress.attr('value', count);
              $list.children().each(function() {
                var thatScore = $(this).find('.score').text();
                if (!appended && thatScore <= score) {
                  $(this).before($item);
                  appended = true;
                }
              });
              if (!appended) {
                $list.append($item);
              }
            }
          });
        });
      }
    });
    return false;
  });
})
