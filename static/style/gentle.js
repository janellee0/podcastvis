window.onkeydown = function(ev) {
    if(ev.keyCode == 32) {
        ev.preventDefault();
        $a.pause();
    }
}

function _get(url, cb) {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", url, true);
	xhr.onload = function() {
		cb(this.responseText);
	}
	xhr.send();
}

function _get_json(url, cb) {
	_get(url, function(dat) {
		cb(JSON.parse(dat));
	});
}

function highlight_word() {
    var t = $a.currentTime;
    // XXX: O(N); use binary search
    var hits = wds.filter(function(x) {
        return (t - x.start) > 0.01 && (x.end - t) > 0.01;
    }, wds);
    var next_wd = hits[hits.length - 1];
    if(cur_wd != next_wd) {
        updateView(cur_wd);
        var active = document.querySelectorAll('.active');
        for(var i = 0; i < active.length; i++) {
            active[i].classList.remove('active');
        }
        if(next_wd && next_wd.$div) {
            next_wd.$div.classList.add('active');
        }
    }
    cur_wd = next_wd;
    window.requestAnimationFrame(highlight_word);
}
window.requestAnimationFrame(highlight_word);

// helper function to highlight words with queries
function visualized(entities_to_visualize, word, startOffset) {
	for(var i = 0; i < entities_to_visualize.length; i++) {
		if ((entities_to_visualize[i]["word"] == word) & (entities_to_visualize[i]["start"] == startOffset+1)) {
			console.log(word);
			return true;
		}
	}
	return false;
}

function add_elements(location_response) {
  transcript_location = "static/data/" + getParameterByName("podcast") + "/" + getParameterByName("podcast") + "_gentle_output.json";
	_get_json(transcript_location, function(ret) {
		var locations = location_response;
		console.log(locations);
		var $trans = document.getElementById("transcript");
		var $a = document.getElementById("audio");
		wds = ret['words'];
		transcript = ret['transcript'];
		$trans.innerHTML = '';
		var currentOffset = 0;
		wds.forEach(function(wd, index) {
			if(wd.case == 'not-found-in-transcript') {
				var txt = ' ' + wd.word;
				var $plaintext = document.createTextNode(txt);
				$trans.appendChild($plaintext);
				return;
			}
			// Add non-linked text
			if(wd.startOffset > currentOffset) {
				var txt = transcript.slice(currentOffset, wd.startOffset);
				var $plaintext = document.createTextNode(txt);
				$trans.appendChild($plaintext);
				currentOffset = wd.startOffset;
			}
			var $wd = document.createElement('span');
			var txt = transcript.slice(wd.startOffset, wd.endOffset);
			if (visualized(locations, txt, wd.startOffset)) {
			    // if (txt !== "of") {
			    // 	$wd.className = "highlight";
			    // }
			    $wd.className = "highlight";
			}
			$wd.innerHTML = txt;
			wd.$div = $wd;
			if(wd.start !== undefined) {
				$wd.className += ' success';
			}
			$wd.onclick = function() {
				if(wd.start !== undefined) {
					console.log(wd.start, wd.index);
					$a.currentTime = wd.start;
					$a.play();
				}
			};
			$trans.appendChild($wd);
			currentOffset = wd.endOffset;
		});
		var txt = transcript.slice(currentOffset, transcript.length);
		var $plaintext = document.createTextNode(txt);
		$trans.appendChild($plaintext);
		currentOffset = transcript.length;
	});
}
