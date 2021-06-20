var activeTab = 'resultDisplayHtmlTable';

function showResults(tabName) {
    $('.tabcontent').hide();
    $('.tablinks').removeClass('active');
    $('#' + tabName).show();
    $('#' + tabName + "Tab").addClass('active');
    activeTab = tabName;
}

//***  https://stackoverflow.com/questions/23048550/how-to-copy-a-divs-content-to-clipboard-without-flash/38672314#38672314
function copyToClipboard(containerid) {
    var textarea = document.createElement('textarea')
    textarea.id = 'temp_element'
    textarea.style.height = 0
    document.body.appendChild(textarea)
    textarea.value = document.getElementById(containerid).innerText
    var selector = document.querySelector('#temp_element')
    selector.select()
    document.execCommand('copy')
    document.body.removeChild(textarea);

    $('#copyToClipboardBtn').attr('title', 'Copied!').tooltip('fixTitle').tooltip('show');
    setTimeout(function(){
        $('#copyToClipboardBtn').tooltip('hide').attr('data-original-title', 'Copy to clipboard');
    }, 2000);
}

function showPresetOptions() {
    $('#presetOptionsTrigger').hide();
    $('#presetOptionsDisplay').show();
}
function hidePresetOptions() {
    $('#presetOptionsTrigger').show();
    $('#presetOptionsDisplay').hide();
}

function showCustomTableOptions() {
    $('#customTableOptionsTrigger').hide();
    $('#customTableOptionsDisplay').show();
}
function hideCustomTableOptions() {
    if ($('#useCustomTableOptions').is(':checked')) {
        $('#customTableOptionsTrigger').show();
    } else {
        $('#customTableOptionsTrigger').hide();
    }
    $('#customTableOptionsDisplay').hide();
}

function updateCustomTableOptionsDisplay() {
    if ($('#useCustomTableOptions').is(':checked')) {
        showCustomTableOptions();
    } else {
        hideCustomTableOptions();
    }
}

function sortListElements(elementSelector) {
    var items = $(elementSelector + ' > li').get();
    items.sort(function(a,b){
      var keyA = $(a).text();
      var keyB = $(b).text();

      if (keyA < keyB) return -1;
      if (keyA > keyB) return 1;
      return 0;
    });
    var ul = $(elementSelector);
    $.each(items, function(i, li){
      ul.append(li); /* This removes li from the old spot and moves it */
    });
}

//*** https://stackoverflow.com/a/901144
function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function loadPreset(preset) {
    if (preset.name) {
        $('#newPresetName').val(preset.name);
    }
    $('#builder-basic').queryBuilder('setRules', preset.ruleSet);
    if (preset.useCustomTableOptions == 1) {
        $("#useCustomTableOptions").prop('checked', true);
        if (preset.sortBy) { $("#sortBy").val(preset.sortBy); }
        $("#tableHeader").val(preset.tableHeader);
        $("#tableCaption").val(preset.tableCaption);
        $("#tableClassNames").val(preset.tableClassNames);
        setActiveTableColumns(preset.tableColumnList);
    } else {
        $("#useCustomTableOptions").prop('checked', false);
    }
    updateCustomTableOptionsDisplay();
    $('.submit-query').click();
}

function clearActiveTableColumns(refresh=true) {
    var listEntries = $("#selectedColumns").children('li').get().reverse();
    for (eIdx in listEntries) {
        $("#availableColumns").prepend($(listEntries[eIdx]));
    }
    if (refresh) {
        $("#selectedColumns").sortable("refresh");
        $("#availableColumns").sortable("refresh");
    }
}

function setActiveTableColumns(colList) {
    clearActiveTableColumns(false);
    for (idx in colList) {
        $('li[colName="' + colList[idx] + '"]').each(function(){
            $("#selectedColumns").append($(this));
        });
    }
    sortListElements("#availableColumns");
    $("#selectedColumns").sortable("refresh");
    $("#availableColumns").sortable("refresh");
}

function displayAvailablePresets(pageType = "item") {
    presetHtml = '<table cellspacing="0" cellpadding="0" border="0">\n';

    localPresetList = getLocalPresetList(pageType);
    for (idx in localPresetList) {
        preset = localPresetList[idx];
        presetHtml += "<tr class='presetLocal'>";
        presetHtml += '<td class="presetActions">';
        presetHtml +=   '<div class="btn-group pull-right">';
        presetHtml +=     '<button class="btn btn-xs btn-danger" onclick="deleteLocalPresetByName(\'' + escapeHtml(preset.name) + '\', \'' + pageType + '\'); return false;"><i class="glyphicon glyphicon-trash"></i> Delete</button>';
        presetHtml +=     '<button class="btn btn-xs btn-success" onclick="loadLocalPresetByName(\'' + escapeHtml(preset.name) + '\', \'' + pageType + '\'); return false;"><i class="glyphicon glyphicon-cloud-download"></i> Load</button>';
        presetHtml +=   '</div>';
        presetHtml += '</td>';
        presetHtml += "<td class='presetName'>" + escapeHtml(preset.name) + "</td>";
        presetHtml += "</tr>";
    }

    for (idx in presetList) {
        preset = presetList[idx];
        presetHtml += "<tr class='presetServer'>";
        presetHtml += '<td class="presetActions">';
        presetHtml +=   '<div class="btn-group pull-right">';
        presetHtml +=     '<button class="btn btn-xs btn-success" onclick="loadBuiltInPresetByName(\'' + escapeHtml(preset.name) + '\'); return false;"><i class="glyphicon glyphicon-cloud-download"></i> Load</button>';
        presetHtml +=   '</div>';
        presetHtml += '</td>';
        presetHtml += "<td class='presetName'>" + escapeHtml(preset.name) + "</td>";
        presetHtml += "</tr>";
    }
    presetHtml += '</table>\n';

    $("#presetList").html(presetHtml);
}

function escapeHtml(unsafe) {
	unsafe = "" + unsafe;
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function makePresetFromCurrentConfig() {
    var preset = false;
    var result = $('#builder-basic').queryBuilder('getRules');

    if (!$.isEmptyObject(result)) {
        var colList = [];
        $("#selectedColumns li").each(function(){
            colList.push($(this).attr("colName"));
        });

        preset = {};
        preset.name = $('#newPresetName').val();
        preset.ruleSet = result;
        preset.useCustomTableOptions = $("#useCustomTableOptions").is(":checked") ? 1 : 0;
        if (preset.useCustomTableOptions == 1) {
            preset.sortBy = $("#sortBy").val();
            preset.tableHeader = $("#tableHeader").val();
            preset.tableCaption = $("#tableCaption").val();
            preset.tableClassNames = $("#tableClassNames").val();
            preset.tableColumnList = colList;
        } else {
            preset.sortBy = '';
            preset.tableHeader = '';
            preset.tableCaption = '';
            preset.tableClassNames = '';
            preset.tableColumnList = [];
        }
    }

    return preset;
}

function loadBuiltInPresetByName(presetName) {
    for (idx in presetList) {
        if (presetList[idx].name == presetName) {
            loadPreset(presetList[idx]);
            return true;
        }
    }
    console.log("Built-in preset [" + presetName + "] not found.");
    return false;
}

function loadLocalPresetByName(presetName, pageType="item") {
    var localPresetList = getLocalPresetList(pageType);
    for (idx in localPresetList) {
        if (localPresetList[idx].name == presetName) {
            loadPreset(localPresetList[idx]);
            return true;
        }
    }
    console.log("Local preset [" + presetName + "] not found.");
    return false;
}

function getLocalPresetList(pageType="item") {
    var localPresetListJson = window.localStorage.getItem(pageType + "PresetList");
    try {
        var localPresetList = JSON.parse(localPresetListJson);
    } catch(err) {}

    if (localPresetList) {
        return localPresetList;
    }
    return [];
}

function deleteLocalPresetByName(presetName, pageType="item") {
    if (confirm("Are you sure you want to delete this preset?  This cannot be undone.")) {
        var localPresetList = getLocalPresetList(pageType);
        var found = false;
        for (var idx = 0; idx < localPresetList.length; idx++) {
            if (localPresetList[idx].name == presetName) {
                localPresetList.splice(idx, 1);
                found = true;
                break;
            }
        }

        if (found) {
            saveLocalPresetList(localPresetList, pageType);
            displayAvailablePresets(pageType);
        } else {
            console.log("Delete local preset [" + presetName + "] failed.  Preset not found.");
        }
    }

    return true;
}

function outputLocalPresetsToConsole(pageType="item") {
    var jsonStr = localStorage.getItem(pageType + "PresetList");
    var presetList = JSON.parse(jsonStr);
    for (var i in presetList) {
        console.log(JSON.stringify(presetList[i]));
    }
}

function saveNewLocalPreset(presetName, pageType="item") {
    var rtnVal = false;

    if (presetName) {
        var presetElem = $(".addPresetSection span");
        presetElem.removeClass('has-error');

        var myPreset = makePresetFromCurrentConfig();
        if (myPreset) {
            var localPresetList = getLocalPresetList(pageType);
            myPreset.name = presetName;
            var found = false;
            for (var idx = 0; idx < localPresetList.length; idx++) {
                if (localPresetList[idx].name == presetName) {
                    localPresetList[idx] = myPreset;
                    found = true;
                }
            }
            if (!found)  localPresetList.push(myPreset);
            rtnVal = saveLocalPresetList(localPresetList, pageType);
            if (rtnVal) {
                sortListElements("#availableColumns");

                displayAvailablePresets(pageType);
                $("tr.presetLocal .presetName").each(function(){
                    if ($(this).text() == presetName) {
                        var rowElem = $(this).parent();
                        rowElem.addClass('newlyAddedPreset', 500);
                        setTimeout(function(){
                            rowElem.removeClass('newlyAddedPreset', 500);
                        }, 1750);
                    }
                });
            }
        }
    } else {
        var presetElem = $(".addPresetSection span");
        presetElem.addClass('has-error');
    }
    return rtnVal;
}

function saveLocalPresetList(localPresetList, pageType="item") {
    window.localStorage.setItem(pageType+ "PresetList", JSON.stringify(localPresetList));
    return true;
}

function displayShortenedUrl(fullUrl) {
    scriptUrl = "/ajax/getShortenedUrl?" + $.param({ url: fullUrl });

    $.ajax({
        type: "GET",
        url: scriptUrl,
        dataType: "json",
        timeout: 5000,
        success: function (d)  {
            console.log(d);
            alert(d);
        },
        error: function ()  {
            alert(fullUrl);
        },
    });
}

function showCurrentPreset() {
    showPreset(makePresetFromCurrentConfig());
}

function showPreset(preset) {
    console.log(JSON.stringify(preset, null, 2));
    alert(JSON.stringify(preset));
}

function showRuleSet() {
    var result = $('#builder-basic').queryBuilder('getRules');

    if (!$.isEmptyObject(result)) {
        console.log(JSON.stringify(result, null, 2));
        alert(JSON.stringify(result));
    }
}

function resetFloatingTableHeaders() {
    /*
    var $win = $(window),
      $table = $('table.floatheader'),
      $thead = $table.children('thead'),
      $tfoot = $table.children('tfoot'),
      $caption = $table.children('caption'),
      $cells = $thead.children().children().add($caption);

    $win.off('scroll');
    $win.on('scroll', function() {
      var bottom = $table.position().top +
            $table.height() -
            $thead.height() -
            ($tfoot.height() || 0),
        delta = $win.scrollTop() -
            $thead.offset().top +
            $caption.outerHeight(),
        // include border thickness (minus 2)
        vertPos = (delta < 0 || delta > bottom ? 0 : delta - 2);
      $cells.css("transform", "translate(0px," + vertPos + "px)");
    });
    */
}


function areSpoilersActiveInRuleset(ruleSet) {
    var spoilersActive;

    if (ruleSet.condition == "OR" && ruleSet.rules.length == 1) {
        ruleSet.condition = "AND";  //*** Treat a single rule as an and section
    }

    var nonHiddenRulesFound = false;
    var hiddenRulesFound = false;
    for (var i = 0; i < ruleSet.rules.length; i++) {
        rule = ruleSet.rules[i];
        if (rule.rules) {
            nonHiddenRulesFound = true;
            var r = areSpoilersActiveInRuleset(rule);
            if (ruleSet.condition == "AND") {
                if (r === true) {
                    spoilersActive = true;
                } else if (r === false) {
                    spoilersActive = false;
                    break;
                }
            } else {
                if (r === true) {
                    spoilersActive = true;
                    break;
                }
            }
        } else if (rule.id == 'ItemUtils.IsItemHidden' || rule.id == 'ShipUtils.IsShipHidden') {
            hiddenRulesFound = true;
            if (ruleSet.condition == "AND") {
                if (rule.value === true) {
                    spoilersActive = true;
                } else  {
                    spoilersActive = false;
                    break;
                }
            } else {
                if (rule.value === true) {
                    spoilersActive = true;
                    break;
                }
            }
        } else {
            nonHiddenRulesFound = true;
        }
    }

    if (ruleSet.condition == "OR" && spoilersActive === undefined)
        if (hiddenRulesFound && !nonHiddenRulesFound)
            spoilersActive = false;

    return spoilersActive;
}


$( document ).ready(function() {
    if (window.location.pathname.indexOf('shipFinder') != -1) {
        var defaultRuleset = {"condition":"AND","rules":[{"id":"ShipUtils.IsShipHidden","field":"ShipUtils.IsShipHidden","type":"boolean","input":"radio","operator":"equal","value":false}],"valid":true};
    } else {
        var defaultRuleset = {"condition":"AND","rules":[{"id":"ItemUtils.IsItemHidden","field":"ItemUtils.IsItemHidden","type":"boolean","input":"radio","operator":"equal","value":false}],"valid":true};
    }

    var queryBuilderConfig = {
    	'plugins': [ 'bt-tooltip-errors' ],
    	'filters': filterList,
    	'rules': defaultRuleset,
    };
	$('#builder-basic').queryBuilder(queryBuilderConfig);
    $('#builder-basic').on('rulesChanged.queryBuilder', function(e) {
        var ruleSet;
        var spoilersActive;
        try {
            ruleSet = $('#builder-basic').queryBuilder('getRules');
        } catch (e) {}

        if (ruleSet && ruleSet.valid) {
            var spoilersActive = areSpoilersActiveInRuleset(ruleSet);
            if (spoilersActive === false) {
                console.log("No spoilers here!");
                $("#spoilerAlert").hide();
            } else {
                console.log("Here there be dragons...");
                $("#spoilerAlert").show();
            }
        }

        console.log(ruleSet);
    });

	//*** SET UP BUTTON ACTIONS
	$('.reset').on('click', function() {
        var target = $(this).data('target');

        hidePresetOptions();

        $('#builder-'+target).queryBuilder('setRules', defaultRuleset);
        $("#useCustomTableOptions").prop('checked', false);
        hideCustomTableOptions();
        $("#tableHeader").val("");
        $("#tableCaption").val("");
        $("#tableClassNames").val("wikitable sortable floatheader");
        $('#newPresetName').val("");
        setActiveTableColumns(["Name","Dmg","ROF","Spd","Lt","Range","Ammo","Energy","Effect","Skill","Image","Type"]);

        return false;
	});

	$('.show-rules').on('click', showRuleSet);
	$('.show-preset').on('click', showCurrentPreset);

	$('.show-url').on('click', function() {
        var preset = makePresetFromCurrentConfig();
        if (!$.isEmptyObject(preset)) {
            var url = window.location.origin + window.location.pathname;
            url += "?preset=" + encodeURIComponent(JSON.stringify(preset));
            displayShortenedUrl(url);
        }
        return false;
	});

	$('.submit-query-item').on('click', function() {
        var result = makePresetFromCurrentConfig();

        if (!$.isEmptyObject(result)) {
            $('#resultDisplayHtmlTable').html('Loading...');
            $('#resultDisplayWiki').html('Loading...');
            $('#resultDisplayJson').html('Loading...');
            $('#resultCount').html('&nbsp;');

            jQuery.ajax({
                url: "/ajax/getItemPresetList",
                type: "POST",
                data: JSON.stringify(result),
                dataType: "script",
                success: function(){ $("table.sortable").tablesorter({}); resetFloatingTableHeaders(); },
            });

            hideCustomTableOptions();
            hidePresetOptions();
            sortListElements("#availableColumns");
            showResults("resultDisplayHtmlTable");
        }

        return false;
	});

	$('.submit-query-ship').on('click', function() {
        var result = makePresetFromCurrentConfig();

        if (!$.isEmptyObject(result)) {
            $('#resultDisplayHtmlTable').html('Loading...');
            $('#resultDisplayWiki').html('Loading...');
            $('#resultDisplayJson').html('Loading...');
            $('#resultCount').html('&nbsp;');

            jQuery.ajax({
                url: "/ajax/getShipPresetList",
                type: "POST",
                data: JSON.stringify(result),
                dataType: "script",
                success: function(){ $("table.sortable").tablesorter({}); resetFloatingTableHeaders(); },
            });

            hideCustomTableOptions();
            hidePresetOptions();
            showResults("resultDisplayHtmlTable");
        }

        return false;
	});

    //*** Show the html results tab by default on page load
    showResults('resultDisplayHtmlTable');

    //*** Set up the click event for the custom table options checkbox, and ensure the display is correct
    $('#useCustomTableOptions').click(updateCustomTableOptionsDisplay);
    updateCustomTableOptionsDisplay();

    //*** Enable tooltip displays
    $('[data-toggle="tooltip"]').tooltip({
        trigger : 'hover'
    });

    //*** Enable table column displays
    $( "#availableColumns, #selectedColumns" ).sortable({
      connectWith: ".connectedColumnList"
    }).disableSelection();

    jQuery.ajax({ url: "/RefreshData" });
});
