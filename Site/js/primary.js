function getUserSearch(userSearchString) {
	$.getJSON( "/api/v1/players/search?userToSearchFor=" + userSearchString + "&limit=50", function( data ) {
		var items = [];
		$.each( data, function (index, value) {
			if (value.IconName != null) {
				profilePicturePath = "/images/avatars/" + value.IconName + ".avif"
				ProfilePictureAlt = value.IconName
				
			} else {
				profilePicturePath = "/images/avatars/cardicon_bot.avif"
				ProfilePictureAlt = "Default Profile Picture"
			}
			items.push( "<tr>" );
			items.push( "<td> <a href='/players/player/" + value.UserID + "?searchString=" + userSearchString + "'><img src='" + profilePicturePath + "' class='rounded' style='height:auto; max-height:6vh;' alt='" + ProfilePictureAlt + "'>" + "" + "</img></a></td>" );
			items.push( "<td> <a href='/players/player/" + value.UserID + "?searchString=" + userSearchString + "'>" + value.Nickname + "</a></td>" );
			items.push( "<td> <a href='/players/player/" + value.UserID + "?searchString=" + userSearchString + "'>" + convertTimestamptoTime(value.LastUpdated) + "</a></td>" );
			items.push( "</tr>" );
		});
		$("#searchResponse tbody").html(items.join( "" ))
	});
}

function getUserDetails(userID) {
	uri = "/api/v1/players/details/" + userID
	uri = addUriParameterFromCurrentSite(uri,'timestamp')
	$.getJSON( uri, function( data ) {
		$("#notToBeShown").remove();
		$("#notToBeShown2").remove();
		$("#notToBeShown3").remove();
		$("#titles").remove();
		$("#experienceConvertedInGoldenEagles").remove();
		$("#estimatedCostInGjn").remove();
		if (data[0].IconName != null) {
			$("#profilePicture td img").prop("alt", data[0].IconName)
			$("#profilePicture td img").prop("src", "/images/avatars/" + data[0].IconName + ".avif")
		} else {
			$("#profilePicture td img").prop("alt", "Default Profile Picture")
			$("#profilePicture td img").prop("src", "/images/avatars/cardicon_bot.avif")
		}
		$("#username td").html(data[0].Nickname)
		$("#title td").html(data[0].TitleName)
		if (data[0].Titles.length > 0) {
			$("#title").attr({["data-bs-toggle"]: "collapse",["data-bs-target"]: "#titles",["aria-expanded"]: "false",["aria-controls"]:"titles"})
			let titlesList = "<tr class='collapse' id='titles'><td colspan='3'><div class='card card-body'><ul class='list-group'>"
			$.each( data[0].Titles, function (index, value) {
				if (value == data[0].TitleName) {
					attributes = "class='list-group-item active' aria-current='true'"
				} else {
					attributes = "class='list-group-item'"
				}
				
				titlesList = titlesList + "<li " + attributes + " >" + value + "</li>"
			})
			
			titlesList = titlesList + "</ul></div></td></tr>"
			$("#title").after( titlesList );
			$("#title").after( "<tr class='collapse' id='notToBeShown'></tr>" );
		}
		$("#clan td").html(data[0].ClanName)
		$("#clanTag td").html(data[0].ClanTag)
		$("#clanRole td").html(data[0].ClanRole)
		$("#experience td").html(data[0].Experience.toLocaleString())
		if (data[0].ExperienceConverted >= 0) {
			$("#experienceConverted td").html(data[0].ExperienceConverted.toLocaleString())
		} else {
			$("#experienceConverted td").html((0).toLocaleString())
		}
		goldenEaglesRPCost = Math.ceil((data[0].ExperienceConverted)/45)
		if (data[0].ExperienceConverted > 0) {
			$("#experienceConverted").attr({["data-bs-toggle"]: "collapse",["data-bs-target"]: "#experienceConvertedInGoldenEagles",["aria-expanded"]: "false",["aria-controls"]:"experienceConvertedInGoldenEagles"})
			let experienceConvertedInGoldenEagles = "<tr class='collapse' id='experienceConvertedInGoldenEagles'><td colspan='3'><div class='card card-body'><ul class='list-group'>"
			experienceConvertedInGoldenEagles = experienceConvertedInGoldenEagles + "<li class='list-group-item'>Cost in Golden Eagles: " + goldenEaglesRPCost.toLocaleString() + "</li></ul></div></td></tr>"
			$("#experienceConverted").after( experienceConvertedInGoldenEagles );
			$("#experienceConverted").after( "<tr class='collapse' id='notToBeShown2'></tr>" );
		}
		$("#spadedVehicles td").html(data[0].SpadedVehicles.toLocaleString())
		$("#lastActive td").html(convertTimestamptoTime(data[0].LastDay))
		$("#signupDate td").html(convertTimestamptoTime(data[0].RegisterDay))
		$("#profileStatus td").html(data[0].PenaltyStatus)
		$("#statsLastUpdated td").html(convertTimestamptoTime(data[0].LastUpdated))
		$("#premiumVehicleGoldenEagleCost td").html(data[0].EstimatedGoldCost.toLocaleString())
		goldenEaglesCost = goldenEaglesRPCost + data[0].EstimatedGoldCost
		cost = 0
		cost += (Math.floor(goldenEaglesCost / 25000) * 114)
		goldenEaglesCost = goldenEaglesCost % 25000
		cost += (Math.floor(goldenEaglesCost / 10000) * 49.5)
		goldenEaglesCost = goldenEaglesCost % 10000
		cost += (Math.floor(goldenEaglesCost / 5000) * 24.75)
		goldenEaglesCost = goldenEaglesCost % 5000
		cost += (Math.floor(goldenEaglesCost / 2500) * 16.5)
		goldenEaglesCost = goldenEaglesCost % 2500
		cost += (Math.floor(goldenEaglesCost / 1000) * 6.6)
		goldenEaglesCost = goldenEaglesCost % 1000
		cost += (Math.floor(goldenEaglesCost / 150) * 0.99)
		goldenEaglesCost = goldenEaglesCost % 150
		if (cost > 0) {
			$("#premiumVehicleGoldenEagleCost").attr({["data-bs-toggle"]: "collapse",["data-bs-target"]: "#estimatedCostInGjn",["aria-expanded"]: "false",["aria-controls"]:"estimatedCostInGjn"})
			let estimatedCostInGjn = "<tr class='collapse' id='estimatedCostInGjn'><td colspan='3'><div class='card card-body'><ul class='list-group'>"
			estimatedCostInGjn = estimatedCostInGjn + "<li class='list-group-item'>Estimated cost in GJN (Premiums + converted RP): " + cost.toLocaleString() + "</li></ul></div></td></tr>"
			$("#premiumVehicleGoldenEagleCost").after( estimatedCostInGjn );
			$("#premiumVehicleGoldenEagleCost").after( "<tr class='collapse' id='notToBeShown3'></tr>" );
		}
		
		if (data[0].Vehicles) {
			let tabablePanesWithPlayerStatistics = "<nav><div class='nav nav-tabs' role='tablist'>";
			tabablePanesWithPlayerStatistics += "<button class='nav-link active' id='vehicleCount-tab' data-bs-toggle='tab' data-bs-target='#vehicleCount' type='button' role='tab' aria-controls='vehicleCount' aria-selected='true'>Vehicle Count</button>";
			tabablePanesWithPlayerStatistics += "<button class='nav-link' id='vehicleClassStats-tab' data-bs-toggle='tab' data-bs-target='#vehicleClassStats' type='button' role='tab' aria-controls='vehicleClassStats' aria-selected='false'>Vehicle Class Stats</button>";
			tabablePanesWithPlayerStatistics += "</div><div class='tab-content'>"
			tabablePanesWithPlayerStatistics += "<div class='tab-pane fade show active' id='vehicleCount' role='tabpanel' aria-labelledby='vehicleCount-tab'>"
			tabablePanesWithPlayerStatistics += "<div class='table-responsive'><table class='table table-hover table-striped'>"
			tabablePanesWithPlayerStatistics += "<thead><tr>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Country</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>0-49% of modifications purchased</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>50-99% of modifications purchased</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Spaded</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Premium</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Gift</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Event</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Squadron</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Total</th>"
			tabablePanesWithPlayerStatistics += "</tr></thead><tbody>"
			// Define some values to contain the total amount of vehicles
			totalModificationStatus0 = 0;
			totalModificationStatus1 = 0;
			totalmodificationStatus2 = 0;
			totalPremiumVehicles = 0;
			totalGiftVehicles = 0;
			totalEventVehicles = 0;
			totalClanVehicles = 0;
			totalTotalVehicles = 0;
			$.each( data[0].Vehicles, function (countryIndex, vehicleTypes) {
				// Define some values to contain the total amount of vehicles
				countryModificationStatus0 = 0;
				countryModificationStatus1 = 0;
				countrymodificationStatus2 = 0;
				countryPremiumVehicles = 0;
				countryGiftVehicles = 0;
				countryEventVehicles = 0;
				countryClanVehicles = 0;
				countryTotalVehicles = 0;
				$.each( vehicleTypes, function (index, value) {
					countryModificationStatus0 += value.ModificationStatus0;
					countryModificationStatus1 += value.ModificationStatus1;
					countrymodificationStatus2 += value.ModificationStatus2;
					countryPremiumVehicles += value.PremiumVehicles;
					countryGiftVehicles += value.GiftVehicles;
					countryEventVehicles += value.EventVehicles;
					countryClanVehicles += value.ClanVehicles;
					countryTotalVehicles += value.TotalVehicles;
				})
				totalModificationStatus0 += countryModificationStatus0;
				totalModificationStatus1 += countryModificationStatus1;
				totalmodificationStatus2 += countrymodificationStatus2;
				totalPremiumVehicles += countryPremiumVehicles;
				totalGiftVehicles += countryGiftVehicles;
				totalEventVehicles += countryEventVehicles;
				totalClanVehicles += countryClanVehicles;
				totalTotalVehicles += countryTotalVehicles;
				tabablePanesWithPlayerStatistics += "<tr>"
				tabablePanesWithPlayerStatistics += "<td><img loading='lazy' class='me-1 rounded' style='max-width: 35px' src='/images/uiElements/country_" + countryIndex.toLowerCase() + ".svg' alt='Icon for the country " + countryIndex + "'></img>" + countryIndex + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryModificationStatus0 + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryModificationStatus1 + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countrymodificationStatus2 + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryPremiumVehicles + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryGiftVehicles + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryEventVehicles + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryClanVehicles + "</td>"
				tabablePanesWithPlayerStatistics += "<td>" + countryTotalVehicles + "</td>"
				tabablePanesWithPlayerStatistics += "</tr>"
			});
			tabablePanesWithPlayerStatistics += "<tr class='table-secondary'>"
			tabablePanesWithPlayerStatistics += "<th>Total</th>"
			tabablePanesWithPlayerStatistics += "<td>" + totalModificationStatus0 + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalModificationStatus1 + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalmodificationStatus2 + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalPremiumVehicles + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalGiftVehicles + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalEventVehicles + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalClanVehicles + "</td>"
			tabablePanesWithPlayerStatistics += "<td>" + totalTotalVehicles + "</td>"
			tabablePanesWithPlayerStatistics += "</tr>"
			tabablePanesWithPlayerStatistics += "</tbody></table></div>";
			tabablePanesWithPlayerStatistics += "</div>";
			tabablePanesWithPlayerStatistics += "<div class='tab-pane fade' id='vehicleClassStats' role='tabpanel' aria-labelledby='vehicleClassStats-tab'>";
			tabablePanesWithPlayerStatistics += "<nav><div class='nav nav-tabs' role='tablist'>";
			tabablePanesWithPlayerStatistics += "<button class='nav-link active' id='summaryVehicleClassStats-tab' data-bs-toggle='tab' data-bs-target='#summaryVehicleClassStats' type='button' role='tab' aria-controls='summaryVehicleClassStats' aria-selected='true'>Summary</button>";
			$.each( data[0].MissionsPlayed.pvp_played, function (gamemode, gamemodeStats) {
				tabablePanesWithPlayerStatistics += "<button class='nav-link' id='" + gamemode + "VehicleClassStats-tab' data-bs-toggle='tab' data-bs-target='#" + gamemode + "VehicleClassStats' type='button' role='tab' aria-controls='" + gamemode + "vehicleClassStats' aria-selected='false'>" + gamemode.charAt(0).toUpperCase() + gamemode.slice(1) + " Vehicle Class Stats</button>";
			})
			tabablePanesWithPlayerStatistics += "</div><div class='tab-content'>"
			const summaryVehicleClassStats = {};
			$.each( data[0].MissionsPlayed.pvp_played, function (gamemode, gamemodeStats) {
				tabablePanesWithPlayerStatistics += "<div class='tab-pane fade' id='" + gamemode + "VehicleClassStats' role='tabpanel' aria-labelledby='" + gamemode + "VehicleClassStats-tab'>";
				tabablePanesWithPlayerStatistics += "<div class='table-responsive'><table class='table table-hover table-striped'>"
				tabablePanesWithPlayerStatistics += "<thead><tr>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Vehicle Class</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Time Played (Hours)</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Spawns</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Air Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Ground Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Naval Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>AI Air Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>AI Ground Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>AI Naval Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Air Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Ground Kills</th>"
				tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Naval Kills</th>"
				tabablePanesWithPlayerStatistics += "</tr></thead><tbody>"
				const totalVehicleClassStats = {};
				$.each(gamemodeStats, function (vehicleClass, vehicleClassStats) {
					if (vehicleClass !== "MissionsCompleted" && vehicleClass !== "Victories") {
						if(!summaryVehicleClassStats.hasOwnProperty(vehicleClass)){
							summaryVehicleClassStats[vehicleClass] = {};
						}
						tabablePanesWithPlayerStatistics += "<tr>"
						tabablePanesWithPlayerStatistics += "<td>" + vehicleClass + "</td>"
						$.each(vehicleClassStats, function (vehicleClassStat, vehicleClassStatNumber) {
							if(summaryVehicleClassStats[vehicleClass].hasOwnProperty(vehicleClassStat)){
								summaryVehicleClassStats[vehicleClass][vehicleClassStat] += vehicleClassStatNumber;
							} else {
								summaryVehicleClassStats[vehicleClass][vehicleClassStat] = vehicleClassStatNumber;
							}
							if(totalVehicleClassStats.hasOwnProperty(vehicleClassStat)){
								totalVehicleClassStats[vehicleClassStat] += vehicleClassStatNumber;
							} else {
								totalVehicleClassStats[vehicleClassStat] = vehicleClassStatNumber;
							}
							if (vehicleClassStat == "TimePlayed") {
								vehicleClassStatNumber = Math.floor(vehicleClassStatNumber / 3600);
							}
							tabablePanesWithPlayerStatistics += "<td>" + vehicleClassStatNumber + "</td>"
						})
						tabablePanesWithPlayerStatistics += "</tr>"
					}
				})
				tabablePanesWithPlayerStatistics += "<tr class='table-secondary'>"
				tabablePanesWithPlayerStatistics += "<th>Total</th>"
				$.each(totalVehicleClassStats, function (vehicleClassStat, vehicleClassStatNumber) {
					if (vehicleClassStat == "TimePlayed") {
						vehicleClassStatNumber = Math.floor(vehicleClassStatNumber / 3600);
					}
					tabablePanesWithPlayerStatistics += "<td>" + vehicleClassStatNumber + "</td>"
				})
				tabablePanesWithPlayerStatistics += "</tr>"
				tabablePanesWithPlayerStatistics += "</tbody></table></div>";
				tabablePanesWithPlayerStatistics += "</div>";
			})
			tabablePanesWithPlayerStatistics += "<div class='tab-pane fade show active' id='summaryVehicleClassStats' role='tabpanel' aria-labelledby='summaryVehicleClassStats-tab'>";
			tabablePanesWithPlayerStatistics += "<div class='table-responsive'><table class='table table-hover table-striped'>"
			tabablePanesWithPlayerStatistics += "<thead><tr>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Vehicle Class</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Time Played (Hours)</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Spawns</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Air Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Ground Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Naval Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>AI Air Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>AI Ground Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>AI Naval Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Air Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Ground Kills</th>"
			tabablePanesWithPlayerStatistics += "<th scope='col'>Bot Naval Kills</th>"
			tabablePanesWithPlayerStatistics += "</tr></thead><tbody>"
			totalVehicleClassStats = {};
			$.each(summaryVehicleClassStats, function (vehicleClass, vehicleClassStats) {
				tabablePanesWithPlayerStatistics += "<tr>"
				tabablePanesWithPlayerStatistics += "<td>" + vehicleClass + "</td>"
				$.each(vehicleClassStats, function (vehicleClassStat, vehicleClassStatNumber) {
					if(totalVehicleClassStats.hasOwnProperty(vehicleClassStat)){
						totalVehicleClassStats[vehicleClassStat] += vehicleClassStatNumber;
					} else {
						totalVehicleClassStats[vehicleClassStat] = vehicleClassStatNumber;
					}
					if (vehicleClassStat == "TimePlayed") {
						vehicleClassStatNumber = Math.floor(vehicleClassStatNumber / 3600);
					}
					tabablePanesWithPlayerStatistics += "<td>" + vehicleClassStatNumber + "</td>"
				})
			})
			tabablePanesWithPlayerStatistics += "<tr class='table-secondary'>"
			tabablePanesWithPlayerStatistics += "<th>Total</th>"
			$.each(totalVehicleClassStats, function (vehicleClassStat, vehicleClassStatNumber) {
				if (vehicleClassStat == "TimePlayed") {
					vehicleClassStatNumber = Math.floor(vehicleClassStatNumber / 3600);
				}
				tabablePanesWithPlayerStatistics += "<td>" + vehicleClassStatNumber + "</td>"
			})
			tabablePanesWithPlayerStatistics += "</tr>"
			tabablePanesWithPlayerStatistics += "</tbody></table></div>";
			tabablePanesWithPlayerStatistics += "</div>";
			tabablePanesWithPlayerStatistics += "</div>";
			tabablePanesWithPlayerStatistics += "</div>";
			tabablePanesWithPlayerStatistics += "</div>";
			
			$("#generalPlaySatisticsForPlayer").html(tabablePanesWithPlayerStatistics);
		}
		const queryString = window.location.search;
		const urlParams = new URLSearchParams(queryString);
		$("#userDetailsTimetampButton").html("");
		const timestampLabel = document.createElement("label");
		const timestampButton = document.createElement("button");
		const timestampButtonUnorderedList = document.createElement("ul");
		timestampLabel.innerHTML = "Timestamp:";
		timestampLabel.setAttribute("for", "timestampButton");
		timestampLabel.classList.add("me-2");
		timestampButton.id = "timestampButton";
		if (urlParams.has("timestamp")) {
			timestampButton.innerHTML = convertTimestamptoTime(urlParams.get("timestamp"));
		} else {
			timestampButton.innerHTML = "Timestamp"
		}
		timestampButton.classList.add("btn");
		timestampButton.classList.add("btn-primary");
		timestampButton.classList.add("dropdown-toggle");
		timestampButton.setAttribute("data-bs-toggle", "dropdown");
		timestampButton.setAttribute("aria-expanded", "false");
		timestampButton.setAttribute("type", "button");
		timestampButtonUnorderedList.classList.add("dropdown-menu");
		document.getElementById("userDetailsTimetampButton").appendChild(timestampLabel);
		document.getElementById("userDetailsTimetampButton").appendChild(timestampButton);
		data[0].Timestamps.forEach(element => {
			const timestampButtonListItem = document.createElement("li");
			const timestampButtonElement = document.createElement("a");
			timestampButtonElement.classList.add("dropdown-item");
			timestampButtonElement.innerHTML = convertTimestamptoTime(element);
			timestampButtonElement.setAttribute("onclick", 'GetUserByTimestamp("' + element + '")');
			timestampButtonListItem.appendChild(timestampButtonElement);
			timestampButtonUnorderedList.appendChild(timestampButtonListItem)
		});
		document.getElementById("userDetailsTimetampButton").appendChild(timestampButtonUnorderedList);
	});
}

function requestStatRefresh(userID) {
	$.getJSON( "/api/v1/players/update/" + userID, function( data ) {
		let modalToggle = bootstrap.Modal.getOrCreateInstance(document.getElementById('messageModal'))
		if(data.InQueue == true) {
			$("#messageModalLabel").html("Succesful submission")
			$("#messageModal .modal-dialog .modal-content .modal-body").html(data.Text + "<br><br><p id='statusText'>Site will auto refresh once profile has been updated, estimated time to refresh: </p><p id='countdown'></p>")
			
			var coeff = 1000 * 60;
			var date = new Date();
			var roundedDate = new Date(Math.ceil(date.getTime() / coeff) * coeff)
			roundedDate.setSeconds(roundedDate.getSeconds() + 10)
			var startDate = new Date();
			var secondsBeforeRefresh = Math.round((roundedDate.getTime() - startDate.getTime()) / 1000);
			$("#countdown").html(secondsBeforeRefresh + " Seconds")
			modalToggle.show();
			setInterval(checkForNewStats, 5000, userID, roundedDate)
		} else {
			$("#messageModalLabel").html("Warning")
			$("#messageModal .modal-dialog .modal-content .modal-body").html(data.Text)
			modalToggle.show();
		}
	})
}

function checkForNewStats(userID,expectedEndDate) {
	$.getJSON( "/api/v1/players/update/" + userID, function( data ) {
		if (data.InQueue == true) {
			var startDate = new Date();
			var secondsBeforeRefresh = Math.round((expectedEndDate.getTime() - startDate.getTime()) / 1000);
			if (secondsBeforeRefresh >= 0) {
				$("#countdown").html(secondsBeforeRefresh + " Seconds")
			} else {
				$("#statusText").html("We seem to have underestimated the time to refresh this profile, please allow us a bit more time, the page will refresh once the stats are updated, expectations exceeded by:")
				$("#countdown").html(secondsBeforeRefresh + " Seconds")
			}
		} else {
			location.reload(true)
		}
	})
	
}

function addUriParameterFromCurrentSite(uri,parameter) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	const url = new URL(uri,window.location.origin);
	if (urlParams.has(parameter)) {
		url.searchParams.delete(parameter);
		url.searchParams.append(parameter, urlParams.get(parameter));
	}
	return url.href
}

function getPlayerVehicleStats(userID) {
	uri = "api/v1/players/vehicleStats/" + userID
	uri = addUriParameterFromCurrentSite(uri,'timestamp');
	uri = addUriParameterFromCurrentSite(uri,'country');
	uri = addUriParameterFromCurrentSite(uri,'gamemode');
	uri = addUriParameterFromCurrentSite(uri,'language');
	uri = addUriParameterFromCurrentSite(uri,'vehicletype');
	["Tier","Battlerating","Victories","Defeats","In Session","Spawns","Deaths","Ground Kills","Air Kills","Naval Kills"].forEach(element => {
		uri = addUriParameterFromCurrentSite(uri,"min" + element.replace(/ /g, '').toLowerCase());
		uri = addUriParameterFromCurrentSite(uri,"max" + element.replace(/ /g, '').toLowerCase());
	});

	$.getJSON(uri, function( data ) {
		
		if (data) {
			
			const queryString = window.location.search;
			const urlParams = new URLSearchParams(queryString);
		
			data = data.map( x => {
				
				winPercentage = (Number(x.Victories) / (Number(x.Victories) + Number(x.Defeats)))
				if (isNaN(winPercentage)) {
					winPercentage = 0
				} else if (winPercentage === Infinity) {
					winPercentage = 1
				}
				x.WinPercentage = winPercentage
				
				if (x.GamemodeName == null) {
					x.GamemodeName = "Never_Played"
				}
				
				x.Battlerating = parseFloat(x.Battlerating).toFixed(1)
				
				let array = []
				let killDeath = 0
				let totalKills = 0
				if (urlParams.has(x.VehicleType + "KD")) {
					const Current = urlParams.get(x.VehicleType + "KD")
					array = array.concat(Current.split(','));
					uniqueArray = [...new Set(array)];
					uniqueArray.forEach(element => {
						totalKills += x[element]
					})
					killDeath = totalKills / x.Deaths
				} else {
					switch (x.VehicleType) {
						case "Aircraft":
							killDeath = x.AirKills / x.Deaths
							totalKills = x.AirKills
							break;
						case "Helicopter":
							killDeath = x.GroundKills / x.Deaths
							totalKills = x.GroundKills
							break;
						case "Ship":
							killDeath = x.NavalKills / x.Deaths
							totalKills = x.NavalKills
							break;
						case "Tank":
							killDeath = x.GroundKills / x.Deaths
							totalKills = x.GroundKills
							break;
					}
				}
				
				if (isNaN(killDeath)) {
					killDeath = 0
				} else if (killDeath === Infinity) {
					killDeath = totalKills
				}
				
				x.KillDeathRatio = killDeath
				
				return x
			})
			
			PlayerVehicleStats = data
			
			$("#sortPropertyButton").siblings("ul").html("")
			
			// get a list of properties we want to be able to sort on
			var keys = []
			$.each( data, function (index, value) {
				keys = keys.concat(Object.keys(value));
			});
			
			// deduplicate the properties
			keys = [...new Set(keys)];
			
			keys.forEach(element => {
				if (['VehicleID','VehicleIdentifiyingName','VehicleShortName','VehicleCompressedName','TierRoman','Premium','Gift','Event','Clan','ModificicationStatusText','OperatorCountry','Tags','VehicleType'].includes(element) === false) {
					$("#sortPropertyButton").html(element)
					$("#sortPropertyButton").siblings("ul").append("<li><a class='dropdown-item' onclick='sortProperty(&quot;" + element + "&quot;)'>" + element + "</a></li>")
				}
			});
			if ($("#sortOrderButton svg").hasClass( "bi-sort-down-alt" )) {
				order = "ASC"
			} else {
				order = "DESC"
			}
			createTable($("#sortPropertyButton").html(),order,data)
		} else {
			document.getElementById("playerVehicleStats").innerHTML = "No results found";
			PlayerVehicleStats = null;
			array = null;
		}
	});
}

function orderBy(array, property, order) {
	if (order === "DESC") {
		if(isNaN(array[0][property])){
			let result = array.sort((a, b) =>
				b[property].toLowerCase().localeCompare(a[property].toLowerCase()));
			return result;
		} else {
			let result = array.sort((a, b) =>
				(a[property] < b[property]) ? 1 : (a[property] > b[property]) ? -1 : 0);
			return result;
		}
	} else {
		if(isNaN(array[0][property])){
			let result = array.sort((a, b) =>
				a[property].toLowerCase().localeCompare(b[property].toLowerCase()));
			return result;
		} else {
			let result = array.sort((a, b) =>
				(a[property] > b[property]) ? 1 : (a[property] < b[property]) ? -1 : 0);
			return result;
		}
	}
}

function createTable(propertyToOrderBy = "NationName",order = "ASC",array = null) {
	if(array !== null) {
		PlayerVehicleStats = array
	} else if (PlayerVehicleStats == null) {
		return;
	}
	PlayerVehicleStats = orderBy(PlayerVehicleStats, propertyToOrderBy,order)
	basicHtml = ''
	$.each( PlayerVehicleStats, function (index, value) {
		borderColor = "border-secondary"
		if(value.Premium === 1) {premium = "Yes";borderColor = "border-warning-subtle"} else {premium = "No"}
		if(value.Gift === 1) {gift = "Yes"} else {gift = "No"}
		if(value.Event === 1) {eventVehicle = "Yes"} else {eventVehicle = "No"}
		if(value.Clan === 1) {clan = "Yes";borderColor = "border-success-subtle"} else {clan = "No"}
		basicHtml += "<div class='mt-3 col-xs-12 col-lg-6 col-xxl-4'><table class='table table-striped table-hover text-center table-sm border border-3 " + borderColor + "'><tbody>"
		basicHtml += "<tr class='border-secondary'><td colspan='3'><img loading='lazy' style='background-image: url(&quot;/images/flags/" + value.OperatorCountry + ".avif&quot;);' src='/images/vehicles/" + value.VehicleIdentifiyingName.toLowerCase() + ".avif' class='img-fluid' alt='Image of the " + value.VehicleName + "'></img></td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Vehicle Name:</th><td colspan='2'>" + value.VehicleName + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Vehicle Fullname:</th><td colspan='2'>" + value.VehicleFullName + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Country:</th><td colspan='2'><img loading='lazy' class='me-1 rounded' style='max-width: 25px' src='/images/uiElements/country_" + value.NationName.toLowerCase() + ".svg' alt='Icon for the country " + value.NationName + "'></img>" + value.NationName + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Tier:</th><td colspan='2'>" + value.TierRoman + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Battlerating:</th><td colspan='2'>" + value.Battlerating + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Premium:</th><td colspan='2'>" + premium + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Store/Gift:</th><td colspan='2'>" + gift + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Event:</th><td colspan='2'>" + eventVehicle + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Squadron:</th><td colspan='2'>" + clan + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Victories:</th><td colspan='2'>" + value.Victories + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Defeats:</th><td colspan='2'>" + value.Defeats + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Victory Percentage:</th><td colspan='2'>" + (value.WinPercentage * 100).toFixed(2) + "%</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Sessions with vehicle in lineup:</th><td colspan='2'>" + value.WasInLineup + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Amount of times Spawned:</th><td colspan='2'>" + value.Spawns + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>K/D:</th><td colspan='2'>" + value.KillDeathRatio.toFixed(2) + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Deaths:</th><td colspan='2'>" + value.Deaths + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Ground kills:</th><td colspan='2'>" + value.GroundKills + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Air kills:</th><td colspan='2'>" + value.AirKills + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Naval kills:</th><td colspan='2'>" + value.NavalKills + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Gamemode:</th><td colspan='2'>" + value.GamemodeName + "</td></tr>"
		basicHtml += "<tr class='border-secondary'><th colspan='1' scope='row'>Modification Status:</th><td colspan='2'>" + value.ModificicationStatusText + "</td></tr>"
		basicHtml += "</tbody></table></div>"
	})
	$("#playerVehicleStats").html(basicHtml)
}

function sortOrder() {
	if ($("#sortOrderButton svg").hasClass( "bi-sort-down-alt" )) {
		$("#sortOrderButton").html("<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-up' viewBox='0 0 16 16'><path d='M3.5 12.5a.5.5 0 0 1-1 0V3.707L1.354 4.854a.5.5 0 1 1-.708-.708l2-1.999.007-.007a.5.5 0 0 1 .7.006l2 2a.5.5 0 1 1-.707.708L3.5 3.707zm3.5-9a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5M7.5 6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1zm0 3a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1zm0 3a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1z'/></svg>")
		order = "DESC"
	} else {
		$("#sortOrderButton").html("<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-down-alt' viewBox='0 0 16 16'><path d='M3.5 3.5a.5.5 0 0 0-1 0v8.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 0 0 0-.707-.708L3.5 12.293zm4 .5a.5.5 0 0 1 0-1h1a.5.5 0 0 1 0 1zm0 3a.5.5 0 0 1 0-1h3a.5.5 0 0 1 0 1zm0 3a.5.5 0 0 1 0-1h5a.5.5 0 0 1 0 1zM7 12.5a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5'/></svg>")
		order = "ASC"
	}
	createTable($("#sortPropertyButton").html(),order)
}

function sortProperty(propertyToSortBy) {
	$("#sortPropertyButton").html(propertyToSortBy)
	if ($("#sortOrderButton svg").hasClass( "bi-sort-down-alt" )) {
		order = "ASC"
	} else {
		order = "DESC"
	}
	createTable(propertyToSortBy,order)
}

function convertTimestamptoTime(unixTimestamp) {
    let dateObj = new Date(unixTimestamp * 1000);
	return dateObj.toLocaleString()
}

function isNumber(value) {
  return typeof value === 'number';
}

function returnToSearch(uri) {
	uri = addUriParameterFromCurrentSite(uri,'searchString');
	window.location.href = uri;
}

function getFilters() {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	$.getJSON( "/api/v1/vehicles/vehicleFilters", function( data ) {
		if(data) {
			const checkBoxes = document.createElement("div");
			Object.entries(data).forEach(entry => {
				const [key, value] = entry;
				const dropdownDiv = document.createElement("div");
				const filterLabel = document.createElement("label");
				const filterButton = document.createElement("button");
				const filterButtonUnorderedList = document.createElement("ul");
				dropdownDiv.classList.add("dropdown");
				dropdownDiv.classList.add("m-2");
				filterLabel.innerHTML = key + ":";
				filterLabel.setAttribute("for", "filterButton" + key);
				filterLabel.classList.add("me-2");
				filterButton.id = "filterButton" + key;
				if (urlParams.has(key.toLowerCase())) {
					filterButton.innerHTML = urlParams.get(key.toLowerCase());
				} else {
					filterButton.innerHTML = key
				}
				filterButton.classList.add("btn");
				filterButton.classList.add("btn-primary");
				filterButton.classList.add("dropdown-toggle");
				filterButton.setAttribute("data-bs-toggle", "dropdown");
				filterButton.setAttribute("aria-expanded", "false");
				filterButton.setAttribute("type", "button");
				filterButtonUnorderedList.classList.add("dropdown-menu");
				dropdownDiv.appendChild(filterLabel);
				dropdownDiv.appendChild(filterButton);
				const filterButtonListItem = document.createElement("li");
				const filterButtonElement = document.createElement("a");
				filterButtonElement.classList.add("dropdown-item");
				filterButtonElement.innerHTML = "all/default";
				filterButtonElement.setAttribute("onclick", 'addFilter("' + key.toLowerCase() + '",this);getPlayerVehicleStats(' + userID + ')');
				filterButtonListItem.appendChild(filterButtonElement);
				filterButtonUnorderedList.appendChild(filterButtonListItem)
				value.forEach(element => {
					singleValue = element;
					const filterButtonListItem = document.createElement("li");
					const filterButtonElement = document.createElement("a");
					filterButtonElement.classList.add("dropdown-item");
					filterButtonElement.innerHTML = singleValue;
					filterButtonElement.setAttribute("onclick", 'addFilter("' + key.toLowerCase() + '",this);getPlayerVehicleStats(' + userID + ')');
					filterButtonListItem.appendChild(filterButtonElement);
					filterButtonUnorderedList.appendChild(filterButtonListItem)
					
					if(key == "VehicleType") {
						const checkboxGroup = document.createElement("div");
						checkboxGroup.classList.add("mt-3");
						const checkboxParagraph = document.createElement("p");
						checkboxParagraph.innerHTML = "Type of kills to use for " + singleValue + " K/D calculations:";
						checkboxParagraph.classList.add("mb-1");
						checkboxGroup.append(checkboxParagraph);
						["AirKills","GroundKills","NavalKills"].forEach(element => {
							const checkboxDiv = document.createElement("div");
							checkboxDiv.classList.add("form-check");
							checkboxDiv.classList.add("form-check-inline");
							const checkboxInput = document.createElement("input");
							checkboxInput.classList.add("form-check-input");
							checkboxInput.setAttribute("type", "checkbox");
							checkboxInput.setAttribute("value", "");
							checkboxInput.setAttribute("id", singleValue + element);
							checkboxInput.setAttribute("onclick", 'addKDFilter("' + singleValue + '","' + element + '",this)');
							if (urlParams.has(singleValue + "KD")) {
								const Current = urlParams.get(singleValue + "KD")
								let uniqueArray = [...new Set(Current.split(','))];
								if (uniqueArray.includes(element)) {
									checkboxInput.checked = true;
								}
							}
							checkboxDiv.append(checkboxInput);
							const checkboxLabel = document.createElement("label");
							checkboxLabel.classList.add("form-check-label");
							checkboxLabel.setAttribute("for", singleValue + element);
							checkboxLabel.innerHTML = element;
							checkboxDiv.append(checkboxLabel);
							checkboxGroup.append(checkboxDiv);
						})
						checkBoxes.append(checkboxGroup);
					}
				});
				dropdownDiv.appendChild(filterButtonUnorderedList);
				document.getElementById("filterModalBody").appendChild(dropdownDiv);
			});
			["Tier","Battlerating","Victories","Defeats","In Session","Spawns","Deaths","Ground Kills","Air Kills","Naval Kills"].forEach(element => {
				const valueRangeDiv = document.createElement("div");
				valueRangeDiv.classList.add("input-group");
				valueRangeDiv.classList.add("mb-3");
				const valueRangeInput1 = document.createElement("input");
				valueRangeInput1.setAttribute("type", "number");
				valueRangeInput1.classList.add("form-control");
				valueRangeInput1.setAttribute("placeholder", "0 " + element);
				valueRangeInput1.setAttribute("aria-label", "0 " + element);
				valueRangeInput1.setAttribute("onkeyup", 'addFilterRange("min' + element.replace(/ /g, '').toLowerCase() + '",this);getPlayerVehicleStats(' + userID + ')');
				if (urlParams.has("min" + element.replace(/ /g, '').toLowerCase())) {
					valueRangeInput1.value = urlParams.get("min" + element.replace(/ /g, '').toLowerCase())
				}
				valueRangeDiv.appendChild(valueRangeInput1);
				const splitter = document.createElement("span");
				splitter.classList.add("input-group-text");
				splitter.innerHTML = element + " range";
				valueRangeDiv.appendChild(splitter);
				const valueRangeInput2 = document.createElement("input");
				valueRangeInput2.setAttribute("type", "number");
				valueRangeInput2.classList.add("form-control");
				valueRangeInput2.setAttribute("placeholder", "unlimited " + element);
				valueRangeInput2.setAttribute("aria-label", "unlimited " + element);
				valueRangeInput2.setAttribute("onkeyup", 'addFilterRange("max' + element.replace(/ /g, '').toLowerCase() + '",this);getPlayerVehicleStats(' + userID + ')');
				if (urlParams.has("max" + element.replace(/ /g, '').toLowerCase())) {
					valueRangeInput2.value = urlParams.get("max" + element.replace(/ /g, '').toLowerCase())
				}
				valueRangeDiv.appendChild(valueRangeInput2);
				document.getElementById("filterModalBody").appendChild(valueRangeDiv);
			});
			document.getElementById("filterModalBody").appendChild(checkBoxes);
			$("#filterModal .modal-dialog .modal-content .modal-body").html()
		} else {
			$("#filterModalLabel").html("Warning")
			$("#filterModal .modal-dialog .modal-content .modal-body").html("Unable to get filter information")
		}
	})
}

function addFilterRange(field,item) {
	if (item.value === null || item.value === "") {
		removeUriParameterFromCurrentSite(window.location.href,field)
	} else {
		addUriParameterToCurrentSite(window.location.href,field,item.value)
	}
}

function addFilter(field,item) {
	if (item.innerHTML == "all/default") {
		removeUriParameterFromCurrentSite(window.location.href,field)
		item.parentElement.parentElement.previousElementSibling.innerHTML = item.parentElement.parentElement.previousSibling.previousSibling.innerHTML.replace(":","")
	} else {
		addUriParameterToCurrentSite(window.location.href,field,item.innerHTML)
		item.parentElement.parentElement.previousElementSibling.innerHTML = item.innerHTML
	}
}

function addKDFilter(vehicleType,killType,item) {
	if (document.getElementById(vehicleType + killType).checked) {
		addKDUriParameterToCurrentSite(window.location.href,vehicleType+"KD",killType)
	} else {
		removeKDUriParameterFromCurrentSite(window.location.href,vehicleType+"KD",killType)
	}
	getPlayerVehicleStats(userID)
}

function addUriParameterToCurrentSite(uri,parameter,value) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	const url = new URL(uri,window.location.origin);
	url.searchParams.delete(parameter);
	url.searchParams.append(parameter, value);
	history.pushState(null, document.title, url)
}

function removeUriParameterFromCurrentSite(uri,parameter) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	const url = new URL(uri,window.location.origin);
	url.searchParams.delete(parameter);
	history.pushState(null, document.title, url)
}

function addKDUriParameterToCurrentSite(uri,parameter,value) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	let array = []
	if (urlParams.has(parameter)) {
		const Current = urlParams.get(parameter)
		array = array.concat(Current.split(','));
	}
	array.push(value);
	uniqueArray = [...new Set(array)];
	commaSeperatedValues = uniqueArray.join();
	const url = new URL(uri,window.location.origin);
	url.searchParams.delete(parameter);
	url.searchParams.append(parameter, commaSeperatedValues);
	history.pushState(null, document.title, url)
}

function removeKDUriParameterFromCurrentSite(uri,parameter,value) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	let array = []
	if (urlParams.has(parameter)) {
		const Current = urlParams.get(parameter)
		array = array.concat(Current.split(','));
	}
	array.push(value);
	uniqueArray = [...new Set(array)];
	const index = uniqueArray.indexOf(value);
	uniqueArray.splice(index, 1);
	const url = new URL(uri,window.location.origin);
	url.searchParams.delete(parameter);
	if (uniqueArray.length !== 0) {
		commaSeperatedValues = uniqueArray.join();
		url.searchParams.append(parameter, commaSeperatedValues);
	}
	history.pushState(null, document.title, url)
}

function getGeneralSiteStats() {
	$.getJSON( "/api/v1/general/siteInformation", function( data ) {
		$("#generalSiteStats").children('li').eq(0).html("Stat Pulls: " + data.DataPoints.toLocaleString())
		$("#generalSiteStats").children('li').eq(1).html("Players with stats: " + data.Players.toLocaleString())
		if ((data.DataInBytes / 1000 / 1000 / 1000) > 1) {
			$("#generalSiteStats").children('li').eq(2).html("Database in Gigabyte: " + parseFloat((data.DataInBytes / 1000 / 1000 / 1000).toFixed(2)).toLocaleString())
		} else if ((data.DataInBytes / 1000 / 1000) > 1) {
			$("#generalSiteStats").children('li').eq(2).html("Database in Megabyte: " + parseFloat((data.DataInBytes / 1000 / 1000).toFixed(2)).toLocaleString())
		} else if ((data.DataInBytes / 1000) > 1) {
			$("#generalSiteStats").children('li').eq(2).html("Database in Kilobyte: " + parseFloat((data.DataInBytes / 1000).toFixed(2)).toLocaleString())
		}
	})
}

function GetUserByTimestamp(timestamp) {
	addUriParameterToCurrentSite(window.location.href,"timestamp",timestamp)
	getUserDetails(userID)
	getPlayerVehicleStats(userID)
}

function vehicleSearch(string) {
	addUriParameterToCurrentSite(window.location.href,"searchString",string)
	result = fuse.search(string)
	$("#searchResponse tbody").html();
	var items = [];
	$.each( result, function (index, value) {
		if (value.item.VehicleIdentifiyingName != null) {
			vehiclePicturePath = "/images/vehicles/" + value.item.VehicleIdentifiyingName.toLowerCase() + ".avif"
			vehiclePictureAlt = value.item.VehicleIdentifiyingName
			
		} else {
			vehiclePicturePath = "/images/avatars/cardicon_bot.avif"
			vehiclePictureAlt = "Default Profile Picture"
		}
		items.push( "<tr>" );
		items.push( "<td> <a href='/vehicles/vehicle/" + value.item.VehicleIdentifiyingName + "?searchString=" + string + "'><img loading='lazy' style='height:auto; max-height:10vh; background-size: auto 100%; background-image: url(&quot;/images/flags/" + value.item.OperatorCountry + ".avif&quot;)' src='" + vehiclePicturePath + "' class='rounded' alt='" + vehiclePictureAlt + "'>" + "" + "</img></a></td>" );
		items.push( "<td> <a href='/vehicles/vehicle/" + value.item.VehicleIdentifiyingName + "?searchString=" + string + "'>" + value.item.VehicleFullName + "</a></td>" );
		items.push( "<td> <a href='/vehicles/vehicle/" + value.item.VehicleIdentifiyingName + "?searchString=" + string + "'>" + value.item.NationName + "</a></td>" );
		items.push( "<td> <a href='/vehicles/vehicle/" + value.item.VehicleIdentifiyingName + "?searchString=" + string + "'>" + value.item.Tier + "</a></td>" );
		items.push( "</tr>" );
	});
	$("#searchResponse tbody").html(items.join( "" ));
}

function getVehicleDetails(vehicleIdentifier) {
	uri = "/api/v1/vehicles/vehicleStat/" + vehicleIdentifier
	uri = addUriParameterFromCurrentSite(uri,'gamemode')
	uri = addUriParameterFromCurrentSite(uri,'gameupdateid')
	$.getJSON( uri, function( data ) {
		$("#vehiclePicture td img").prop("alt", data[0].VehicleIdentifiyingName	);
		$("#vehiclePicture td img").prop("src", "/images/vehicles/" + data[0].VehicleIdentifiyingName.toLowerCase() + ".avif");
		$("#vehiclePicture td img").prop("style", 'height:auto; max-height:30vh; background-size: auto 100%; background-image: url("/images/flags/' + data[0].OperatorCountry + '.avif")');
		$("#vehicleFullName td").html(data[0].VehicleFullName);
		$("#vehicleType td").html(data[0].VehicleType);
		$("#tier td").html(data[0].Tier);
		$("#country td").html(data[0].NationName);
		$("#operatorNation td").html(data[0].OperatorName);
		$("#ownedByUniqueUsers td").html(parseInt(data[0].OwnedByUniqueUsers).toLocaleString());
		$("#playedByUniqueUsers td").html(parseInt(data[0].PlayedByUniqueUsers).toLocaleString());
		$("#spawns td").html(parseInt(data[0].Spawns).toLocaleString());
		$("#deaths td").html(parseInt(data[0].Deaths).toLocaleString());
		$("#experienceEarned td").html(parseInt(data[0].ExperienceEarned).toLocaleString());
		$("#silverlionsEarned td").html(parseInt(data[0].SilverLionsEarned).toLocaleString());
		$("#groundKills td").html(parseInt(data[0].GroundKills).toLocaleString());
		$("#airKills td").html(parseInt(data[0].AirKills).toLocaleString());
		$("#navalKills td").html(parseInt(data[0].NavalKills).toLocaleString());
		$("#inLineup td").html(parseInt(data[0].WasInLineup).toLocaleString());
		$("#defeats td").html(parseInt(data[0].Defeats).toLocaleString());
		$("#victories td").html(parseInt(data[0].Victories).toLocaleString());
		
		winPercentage = (Number(data[0].Victories) / (Number(data[0].Victories) + Number(data[0].Defeats)))
		if (isNaN(winPercentage)) {
			winPercentage = 0
		} else if (winPercentage === Infinity) {
			winPercentage = 1
		}

		$("#winPercentage td").html(parseFloat((winPercentage * 100).toFixed(2)).toLocaleString() + "%");
	})
}

function getVehicleStatsByUpdate(vehicleIdentifier) {
	uri = "/api/v1/vehicles/vehicleStatsByUpdate/" + vehicleIdentifier
	uri = addUriParameterFromCurrentSite(uri,'gamemode')
	$.getJSON( uri, function( data ) {
		tableWithVehicleStatistics = "<div class='table-responsive'><table class='table table-hover table-striped'>"
		tableWithVehicleStatistics += "<thead><tr>"
		tableWithVehicleStatistics += "<th scope='col'>Update</th>"
		tableWithVehicleStatistics += "<th scope='col'>Players that used this vehicle</th>"
		tableWithVehicleStatistics += "<th scope='col'>Spawns</th>"
		tableWithVehicleStatistics += "<th scope='col'>Deaths</th>"
		tableWithVehicleStatistics += "<th scope='col'>ExperienceEarned</th>"
		tableWithVehicleStatistics += "<th scope='col'>SilverLionsEarned</th>"
		tableWithVehicleStatistics += "<th scope='col'>GroundKills</th>"
		tableWithVehicleStatistics += "<th scope='col'>AirKills</th>"
		tableWithVehicleStatistics += "<th scope='col'>NavalKills</th>"
		tableWithVehicleStatistics += "<th scope='col'>WasInLineup</th>"
		tableWithVehicleStatistics += "<th scope='col'>Defeats</th>"
		tableWithVehicleStatistics += "<th scope='col'>Victories</th>"
		tableWithVehicleStatistics += "</tr></thead><tbody>"
		$.each( data, function (index, stats) {
			tableWithVehicleStatistics += "<tr>"
			tableWithVehicleStatistics += "<td>" + stats.UpdateTitle + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.PlayedByUniqueUsers).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.Spawns).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.Deaths).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.ExperienceEarned).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.SilverLionsEarned).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.GroundKills).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.AirKills).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.NavalKills).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.WasInLineup).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.Defeats).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "<td>" + parseInt(stats.Victories).toLocaleString() + "</td>"
			tableWithVehicleStatistics += "</tr>"
		})
		tableWithVehicleStatistics += "</tbody></table></div>";
		$("#vehicleStatsByUpdate").html(tableWithVehicleStatistics);
	})
}

function getVehicleStatFilters() {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	$.getJSON( "/api/v1/vehicles/vehicleFilters", function( data ) {
		Object.entries(data).forEach(entry => {
			const [key, value] = entry;
			if (key == "Gamemode") {
				const dropdownDiv = document.createElement("div");
				const filterLabel = document.createElement("label");
				const filterButton = document.createElement("button");
				const filterButtonUnorderedList = document.createElement("ul");
				dropdownDiv.classList.add("dropdown");
				dropdownDiv.classList.add("m-2");
				filterLabel.innerHTML = key + ":";
				filterLabel.setAttribute("for", "filterButton" + key);
				filterLabel.classList.add("me-2");
				filterButton.id = "filterButton" + key;
				if (urlParams.has(key.toLowerCase())) {
					filterButton.innerHTML = urlParams.get(key.toLowerCase());
				} else {
					filterButton.innerHTML = "realistic"
				}
				filterButton.classList.add("btn");
				filterButton.classList.add("btn-primary");
				filterButton.classList.add("dropdown-toggle");
				filterButton.setAttribute("data-bs-toggle", "dropdown");
				filterButton.setAttribute("aria-expanded", "false");
				filterButton.setAttribute("type", "button");
				filterButtonUnorderedList.classList.add("dropdown-menu");
				dropdownDiv.appendChild(filterLabel);
				dropdownDiv.appendChild(filterButton);
				value.forEach(element => {
					singleValue = element;
					const filterButtonListItem = document.createElement("li");
					const filterButtonElement = document.createElement("a");
					filterButtonElement.classList.add("dropdown-item");
					filterButtonElement.innerHTML = singleValue;
					filterButtonElement.setAttribute("onclick", 'addVehicleFilter("' + key.toLowerCase() + '",this)');
					filterButtonListItem.appendChild(filterButtonElement);
					filterButtonUnorderedList.appendChild(filterButtonListItem)
				})
				dropdownDiv.appendChild(filterButtonUnorderedList);
				document.getElementById("vehicleButtons").appendChild(dropdownDiv);
			}
		})
	})
}

function addVehicleFilter(field,item) {
	addUriParameterToCurrentSite(window.location.href,field,item.innerHTML)
	item.parentElement.parentElement.previousSibling.innerHTML = item.innerHTML
	getVehicleDetails(vehicleIdentifier);
	getVehicleStatsByUpdate(vehicleIdentifier);
}

function rarestTitles() {
	$.getJSON( "/api/v1/players/rarestTitles", function( data ) {
		rarestTitlesTableRows = ""
		$.each( data, function (index, titles) {
			rarestTitlesTableRows += "<tr>"
			rarestTitlesTableRows += "<td><a href='/players/titles/" + titles.TitleIdentifier + "'>" + titles.TitleName + "</a></td>"
			rarestTitlesTableRows += "<td><a href='/players/titles/" + titles.TitleIdentifier + "'>" + (titles.percentageOfPlayersWithTitle * 100).toLocaleString(undefined, {minimumFractionDigits: 3}) + "%</a></td>"
			rarestTitlesTableRows += "</tr>"
		})
		$("#rarestTitles tbody").html(rarestTitlesTableRows);
	})
}

function playersWithTitle(titleIdentifier) {
	$("#headerTitle").html("Top 20 Players with the title " + titleIdentifier + " (Ordered by RP earned):");
	$.getJSON( "/api/v1/players/playersWithTitle/" + titleIdentifier, function( data ) {
		playersWithTitleTableRows = ""
		$.each( data, function (index, players) {
			if (players.IconName != null) {
				profilePicturePath = "/images/avatars/" + players.IconName + ".avif"
				ProfilePictureAlt = players.IconName
				
			} else {
				profilePicturePath = "/images/avatars/cardicon_bot.avif"
				ProfilePictureAlt = "Default Profile Picture"
			}
			playersWithTitleTableRows += "<tr>"
			playersWithTitleTableRows += "<td><a href='/players/player/" + players.UserID + "'><img src='" + profilePicturePath + "' class='rounded' style='height:auto; max-height:6vh;' alt='" + ProfilePictureAlt + "'>" + "" + "</img></a></td>"
			playersWithTitleTableRows += "<td><a href='/players/player/" + players.UserID + "'>" + players.Nickname + "</a></td>"
			playersWithTitleTableRows += "</tr>"
		})
		$("#playersWithTitle tbody").html(playersWithTitleTableRows);
	})
}

function addComparisonSelectors(item,id = 1) {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	
	var comparatorType = item.parentElement.parentElement.previousElementSibling.textContent
	var originalElement = item.parentElement.parentElement.parentElement.parentElement
	var parentElement = originalElement.parentElement
	var siblingArray = Array.from(parentElement.children).filter(function (sibling) {
		return sibling !== originalElement;
	});
	siblingArray.forEach((element) => element.remove())
	
	
	
	if (comparatorType == "Player") {
		var dropdownDiv = document.createElement("div");
		var filterLabel = document.createElement("label");
		var filterInput = document.createElement("input");
		dropdownDiv.classList.add("form-group");
		dropdownDiv.classList.add("m-2");
		filterLabel.innerHTML = "Player:";
		filterLabel.setAttribute("for", "playerDropdown" + id);
		filterLabel.classList.add("me-2");
		filterInput.id = "playerDropdown" + id;
		filterInput.classList.add("form-control");
		filterInput.setAttribute("placeholder", "Player");
		filterInput.setAttribute("data-filter", "https://warthunder.mortymail.dk/api/v1/players/search?userToSearchFor=#QUERY#&limit=10&inDatabase=1");
		filterInput.setAttribute("type", "text");
		dropdownDiv.appendChild(filterLabel);
		dropdownDiv.appendChild(filterInput);
		
		parentElement.appendChild(dropdownDiv);
		
		$('#' + 'playerDropdown' + id).autocomplete({
			preProcess(el){
				var array = []
				el.forEach(user => {
					array.push(user.ClanTag + " " + user.Nickname + " (" + user.UserID + ")")
				})
				return array
			}
		})
		$('#' + 'playerDropdown' + id).on('pick.bs.autocomplete', e => {
			let userID = e.item.textContent.split(/\(|\)/)[1]
			addUriParameterToCurrentSite(window.location.href,"userID" + id,userID)
		})
		
		
	} else {
		
	}
}