/*! 
 * Index
 * 
 * -- Counting Stars
 * -- Commitment (Chef-OpenStack) ** For demo only **
 * -- Milestones (Chef-OpenStack) ** For demo only **
 * -- Pull Requests (Chef-OpenStack) ** For demo only **
 * -- Commitment (Jumpgate) ** Hidden until repo goes public **
 * -- Milestones (Jumpgate) ** Hidden until repo goes public **
 * -- Pull Requests (Jumpgate) ** Hidden until repo goes public **
 * 
 */

// Star Count
// A count of all stargazers/members

$.getJSON("https://api.github.com/orgs/softlayer/members?callback=?",

function (result) { 
    var members = result.data;
    $(function () {
        $("#stargazers").text(members.length);
    });
});

// Commitment (Chef-OpenStack)
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

// Milestones (Chef-OpenStack)
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

// Release Pegs (Chef-OpenStack)
// Current release peg and when it went into production


var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/releases?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.published_at),
            stampRelease = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#release-date').text(stampRelease);
        $('#release-branch').text(latest.target_commitish);
        $('#release-peg').text(latest.tag_name);
    }
});

// Commitment (Jumpgate)
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

// Milestones (Jumpgate)
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

// Release Pegs (Jumpgate)
// Current release peg and when it went into production

/* Hidden until repo goes public

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/releases?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.published_at),
            stampRelease = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#release-date').text(stampRelease);
        $('#release-branch').text(latest.target_commitish);
        $('#release-peg').text(latest.tag_name);
    }
});     */