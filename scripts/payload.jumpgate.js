// Milestones
// Fetch date and title of latest milestone

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) {
            $('#milestone-status').hide();
        } else {
            $('#milestone-status').show();

            var stamp = new Date(latest.due_on),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#milestone-date').text(stampString);
            $('#milestone-title').text(latest.title);
        }
    }
});

// Commitments
// Fetch date for last commit

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) {
            $('#commit-status').hide();
        } else {
            $('#commit-status').show();

            var stamp = new Date(latest.commit.committer.date),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#commit-date').text(stampString);
        }
    }
});

// Pull Requests
// Fetch # of pull requests

$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/pulls?state=closed?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) {
            $('#pull-status').hide();
        } else {
            $('#pull-status').show();
            $('#closed-pulls').text(latest.number);
        }
    }
});