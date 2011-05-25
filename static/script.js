function getUserURL(user) {
  return 'http://www.last.fm/user/' + user;
}

function getUserLink(user) {
  var a = document.createElement('a');
  a.setAttribute('href', getUserURL(user));
  a.setAttribute('target', '_blank');
  a.appendChild(document.createTextNode(user));
  return a
}

$(document).ready(function() {
  $('#the-form').submit(function() {
    var user = $('#username').val();
    var url = '/friends?user=' + user;
    $('#username').val('');
    $('#status-bar').empty();
    $('#friend-list').empty();
    $.ajax({
      url: url,
      success: function(data) {
        var friends = $.parseJSON(data);
        var count = 0;
        $('#status-bar').append('Processed <span id="friend-number">0</span> of '+friends.length+' friends for '+getUserLink(user));
        $(friends).each(function(i, friend) {
          $.ajax({
            url: '/compare?user='+user+'&friend='+friend,
            success: function (data) {
              var appended = false;
              var score = $.parseJSON(data);
              var item = document.createElement('li');
              item.appendChild(getUserLink(friend));
              var span = document.createElement('span');
              span.setAttribute('class', 'score');
              span.appendChild(document.createTextNode(score));
              item.appendChild(document.createTextNode(' '));
              item.appendChild(span);
              $('#friend-number').empty().append(++count);
              //$('#friend-list').append(item);
              var $list = $('#friend-list');
              $list.children().each(function() {
                var thatScore = $(this).find('.score').text();
                console.log(thatScore+' '+score);
                if (!appended && thatScore <= score) {
                  $(this).before(item);
                  appended = true;
                }
              });
              if (!appended) {
                $list.append(item);
              }
            }
          });
        });
      }
    });
    return false;
  });
})
