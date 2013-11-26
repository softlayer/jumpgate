// The # of active members/stargazers

$.getJSON("https://api.github.com/orgs/softlayer/members?callback=?",

function (result) {
    var members = result.data;
    $(function () {
        $("#num-members").text(members.length);
    });
});

// The last commit pushed up and who did it (Chef-OpenStack)
// FOR DEMO PURPOSES UNTIL THE JUMPGATE REPO IS PUBLIC 

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#gitdate').text(stampString);
        $('#gitcommitter').text(latest.author.login);
    }
});

// The next milestone date and title (Chef-OpenStack)
// FOR DEMO PURPOSES UNTIL THE JUMPGATE REPO IS PUBLIC

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#mdate').text(stampString);
        $('#mtitle').text(latest.title);
    }
});


// The last commit pushed up and who did it (Jumpgate)
/* COMMENTTED OUT UNTIL REPO IS MADE PUBLIC

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#gitdate').text(stampString);
        $('#gitcommitter').text(latest.author.login);
    }
});

*/

// The next milestone date and title (Jumpgate)
/* COMMENTTED OUT UNTIL REPO IS MADE PUBLIC 

var month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate() + ', ' + stamp.getFullYear();
        $('#mdate').text(stampString);
        $('#mtitle').text(latest.title);
    }
}); 

*/