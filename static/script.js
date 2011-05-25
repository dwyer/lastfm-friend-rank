function getUserURL(user) {
  return 'http://www.last.fm/user/' + user;
}

function getUserLink(user) {
  return '<a href="'+getUserURL(user)+'" target="_blank">'+user+'</a>';
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
              var score = $.parseJSON(data);
              var item = '<li>'+getUserLink(friend)+' <span style="color:gray;">(<span class="score">'+score+'</span>%)</span></li>';
              $('#friend-number').empty().append(++count);
              $('#friend-list').append(item);
              $('#friend-list').sort({
                sortOn: '.score',
                direction: 'desc',
                sortType: 'number'
              });
            }
          });
        });
      }
    });
    return false;
  });
})
