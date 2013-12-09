// Milestones
// Fetch date and title of last milestone closed

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/milestones?state=closed/callback?",
    dataType: 'jsonp',
    success: function (json) {
        var lastMilestone = json.data[0];
        if (!lastMilestone) {
            $('#milestone-status').hide();
        } else {
            $('#milestone-status').show();

            var stamp = new Date(lastMilestone.due_on),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#milestone-date').text(stampString);
            $('#milestone-title').text(lastMilestone.title);
        }
    }
});

// Commitments
// Fetch date for last commit

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/commits?state=closed/callback?",
    dataType: 'jsonp',
    success: function (json) {
        var lastCommit = json.data[0];
        if (!lastCommit) {
            $('#commit-status').hide();
        } else {
            $('#commit-status').show();

            var stamp = new Date(lastCommit.commit.committer.date),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#commit-date').text(stampString);
        }
    }
});

// Pull Requests
// Fetch # of pull requests

$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/pulls?state=closed/callback?",
    dataType: 'jsonp',
    success: function (json) {
        var countPulls = json.data[0];
        if (!countPulls) {
            $('#pull-status').hide();
        } else {
            $('#pull-status').show();
            $('#closed-pulls').text(countPulls.number);
        }
    }
});
