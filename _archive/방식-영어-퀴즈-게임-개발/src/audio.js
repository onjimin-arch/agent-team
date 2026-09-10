/**
 * audio.js — Web Speech API TTS helper
 * Uses browser built-in speechSynthesis. No external API required.
 */

/**
 * Speak text using the browser's TTS engine.
 * @param {string} text - The text to speak
 * @param {string} [lang="en-US"] - Language code for voice selection
 * @returns {boolean} - Whether speech synthesis is available
 */
function speakWord(text, lang) {
  if (!('speechSynthesis' in window)) return false;
  lang = lang || "en-US";

  window.speechSynthesis.cancel();

  var utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.9;
  utterance.pitch = 1;

  var voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    var enVoice = voices.find(function (v) { return v.lang.indexOf(lang) === 0 && v.name.indexOf("Google") !== -1; }) ||
                  voices.find(function (v) { return v.lang.indexOf(lang) === 0; });
    if (enVoice) utterance.voice = enVoice;
  }

  window.speechSynthesis.speak(utterance);
  return true;
}

function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}