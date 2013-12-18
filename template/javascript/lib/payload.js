// Milestones
// Fetch date and title of last milestone closed

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/project-name/milestones?state=closed/callback?", // Update "project-name" to name of the project in GitHub 
    dataType: 'jsonp',
    success: function (json) {
        var lastMilestone = json.data[0];

        var stamp = new Date(lastMilestone.updated_at),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#mdate').text(stampString);
        $('#mtitle').text(lastMilestone.title);
    }
});

// Commitments
// Fetch date for last commit

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/project-name/commits?state=closed/callback?", // Update "project-name" to name of the project in GitHub 
    dataType: 'jsonp',
    success: function (json) {
        var lastCommit = json.data[0];

        var stamp = new Date(lastCommit.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#cdate').text(stampString);
    }
});

// Team/Contributors
// Fetch # of contributors

$.getJSON("https://api.github.com/repos/softlayer/project-name/contributors?callback=?", function (result) { // Update "project-name" to name of the project in GitHub 
    var tcount = result.data;

    $(function () {
        $("#tcount").text(tcount.length);
    });
});

// Repositories
// Fetch # of repos

$.getJSON("https://api.github.com/orgs/project-name/repos?callback=?", function (result) { // Update "project-name" to name of the project in GitHub 
    var rcount = result.data;

    $(function () {
        $("#rcount").text(rcount.length);
    });
});