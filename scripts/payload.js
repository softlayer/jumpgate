/*! 
 * Index
 * 
 * (a) Stars
 * (b) Commitment (Chef-OpenStack) ** For demo only **
 * (c) Milestones (Chef-OpenStack) ** For demo only **
 * (d) Pull Requests (Chef-OpenStack) ** For demo only **
 * (e) Commitment (Jumpgate) ** Hidden until repo goes public **
 * (f) Milestones (Jumpgate) ** Hidden until repo goes public **
 * (g) Pull Requests (Jumpgate) ** Hidden until repo goes public **
 * 
 */

// (a) Stars
// The # of stargazers/members

$.getJSON("https://api.github.com/orgs/softlayer/members?callback=?",

function (result) { 
    var members = result.data;
    $(function () {
        $("#stargazers").text(members.length);
    });
});

// (b) Commitment (Chef-OpenStack)
// Last commit date and who did it

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#commit-date').text(stampString);
        $('#commit-committer').text(latest.author.login);
    }
});

// (c) Milestones (Chef-OpenStack)
// Next milestone date and its title

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#milestone-date').text(stampString);
        $('#milestone-title').text(latest.title);
    }
});

// (d) Pull Requests (Chef-OpenStack)
// Completed pull requests

$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/pulls?state=closed?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;
        $('#closed-pulls').text(latest.number);
    }
});

// (e) Commitment (Jumpgate)
// Last commit date and who did it

/* Hidden until repo goes public

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#commit-date').text(stampString);
        $('#commit-committer').text(latest.author.login);
    }
});     */

// (f) Milestones (Jumpgate)
// Next milestone date and its title

/* Hidden until repo goes public

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#milestone-date').text(stampString);
        $('#milestone-title').text(latest.title);
    }
});     */

// (g) Pull Requests (Jumpgate)
// Completed pull requests

/* Hidden until repo goes public

$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/pulls?state=closed?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;
        $('#closed-pulls').text(latest.number);
    }
});     */