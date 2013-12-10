// Milestones
// Fetch date and title of last milestone closed

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/milestones?state=closed/callback?",
    dataType: 'jsonp',
    success: function (json) {
        var lastMilestone = json.data[0];
        if (!lastMilestone) {
            $('#mstatus').hide();
        } else {
            $('#mstatus').show();

            var stamp = new Date(lastMilestone.updated_at),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#mdate').text(stampString);
            $('#mtitle').text(lastMilestone.title);
        }
    }
});

// Commitments
// Fetch date for last commit

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/commits?state=closed/callback?",
    dataType: 'jsonp',
    success: function (json) {
        var lastCommit = json.data[0];
        if (!lastCommit) {
            $('#cstatus').hide();
        } else {
            $('#cstatus').show();

            var stamp = new Date(lastCommit.commit.committer.date),
                stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
            $('#cdate').text(stampString);
        }
    }
});

// Team/Contributors
// Fetch # of contributors

$.getJSON("https://api.github.com/repos/softlayer/jumpgate/contributors?callback=?", function (result) {
    var tcount = result.data;
    if (!tcount == '') {
        $('#tstatus').hide();
    } else {
        $('#tstatus').show();
        $(function () {
            $("#tcount").text(tcount.length);
        });
    }
});

// Repositories
// Fetch # of repos

$.getJSON("https://api.github.com/orgs/softlayer/repos?callback=?", function (result) {
    var rcount = result.data;
    if (!rcount == '') {
        $('#rstatus').hide();
    } else {
        $('#rstatus').show();
        $(function () {
            $("#rcount").text(rcount.length);
        });
    }
});