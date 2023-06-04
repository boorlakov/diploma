// creator  : WeiDU-Windows/weidu.exe (version 24900)
// argument : ABISHAB.DLG
// game     : D:\other\PTEEPAL\App\GameData
// source   : D:\other\PTEEPAL\App\GameData/DATA/DLGFILES.BIF
// dialog   : D:\other\PTEEPAL\App\GameData\lang\en_us\dialog.tlk
// dialogF  : (none)

BEGIN ~ABISHAB~

IF ~  Global("Know_Abishai","GLOBAL",0)
~ THEN BEGIN 0 // from:
  SAY ~This black-scaled reptile towers to a height of eight feet - its great height, however, is offset by its thin, snake-like frame. A long prehensile tail drags behind it, and its leathery wings are hooked behind its back. A strong vinegary smell emanates from the creature... as well as a certain amount of heat. It seems to be ignoring you.~ /* #3325 */
  IF ~  NearbyDialog("DMorte")
Global("Morte_Abishai_Hive_Quip_1","GLOBAL",0)
~ THEN REPLY ~"Greetings."~ /* #3326 */ DO ~SetGlobal("Morte_Abishai_Hive_Quip_1","GLOBAL",1)
~ EXTERN ~DMORTE~ 131
  IF ~  NearbyDialog("DMorte")
Global("Morte_Abishai_Hive_Quip_1","GLOBAL",1)
~ THEN REPLY ~"Greetings."~ /* #3992 */ EXTERN ~DMORTE~ 133
  IF ~  !NearbyDialog("DMorte")
NearbyDialog("DAnnah")
Global("Annah_Abishai_Hive_Quip_1","GLOBAL",0)
~ THEN REPLY ~"Greetings."~ /* #3993 */ DO ~SetGlobal("Annah_Abishai_Hive_Quip_1","GLOBAL",1)
~ EXTERN ~DANNAH~ 70
  IF ~  !NearbyDialog("DMorte")
NearbyDialog("DAnnah")
Global("Annah_Abishai_Hive_Quip_1","GLOBAL",1)
~ THEN REPLY ~"Greetings."~ /* #3994 */ EXTERN ~DANNAH~ 72
  IF ~  !NearbyDialog("DMorte")
!NearbyDialog("DAnnah")
~ THEN REPLY ~"Greetings."~ /* #3995 */ GOTO 1
  IF ~~ THEN REPLY ~Leave the creature alone.~ /* #7718 */ EXIT
END

IF ~~ THEN BEGIN 1 // from: 11.0 0.4
  SAY ~The creature slowly turns its head down to look at you. Its scaled forehead wrinkles into a frown, then it opens its mouth, giving a low, rasping hiss. You notice that the heat radiating from the creature begins to rise.~ /* #7719 */
  IF ~  !NearbyDialog("DAnnah")
!NearbyDialog("DGrace")
~ THEN REPLY ~"I would speak with you for a moment."~ /* #7720 */ GOTO 2
  IF ~  NearbyDialog("DAnnah")
!NearbyDialog("DGrace")
~ THEN REPLY ~"I would speak with you for a moment."~ /* #7721 */ GOTO 6
  IF ~  NearbyDialog("DGrace")
~ THEN REPLY ~"I would speak with you for a moment."~ /* #7722 */ GOTO 6
  IF ~~ THEN REPLY ~Leave the creature alone.~ /* #7723 */ EXIT
END

IF ~~ THEN BEGIN 2 // from: 1.0
  SAY ~The creature opens its mouth, displaying a row of blackened fangs. Fire begins to dance around the shoulders and arms of the creature as it gives a long, low hiss.~ /* #7724 */
  IF ~~ THEN REPLY ~"Calm yourself! I just want to talk to you."~ /* #7725 */ GOTO 4
  IF ~~ THEN REPLY ~Hiss back.~ /* #7726 */ GOTO 3
  IF ~~ THEN REPLY ~Leave the creature alone.~ /* #7727 */ EXIT
END

IF ~~ THEN BEGIN 3 // from: 5.1 5.0 2.1
  SAY ~The creature roars, then it launches itself at you!~ /* #7728 */
  IF ~~ THEN REPLY ~Defend yourself...~ /* #7730 */ DO ~Enemy()
Attack(Protagonist)
ForceAttack(Protagonist,Myself)
~ EXIT
END

IF ~~ THEN BEGIN 4 // from: 2.0
  SAY ~The creature speaks in a rasping hiss; its voice sounds like two rough stones being scraped together. It hisses for a few moments, its gravelly voice rising and falling.~ /* #7731 */
  IF ~~ THEN REPLY ~"Uh... what?"~ /* #7732 */ GOTO 5
  IF ~~ THEN REPLY ~Leave the creature alone.~ /* #7733 */ EXIT
END

IF ~~ THEN BEGIN 5 // from: 4.0
  SAY ~The creature snarls. "NOTHING to sssay to you, do I." The fiend's eyes narrow to slits. "If ssstay, your warm blood will cover the ssstones."~ /* #7734 */
  IF ~~ THEN REPLY ~"I just wanted to ask you some questions..."~ /* #7735 */ GOTO 3
  IF ~~ THEN REPLY ~"Just try it, and we'll see whose blood covers the street when we're done."~ /* #7736 */ GOTO 3
  IF ~~ THEN REPLY ~Back off and leave the creature alone.~ /* #7737 */ EXIT
END

IF ~~ THEN BEGIN 6 // from: 1.2 1.1
  SAY ~The creature suddenly sniffs the air, then turns away from you with a strange hiss. It seems to have caught some unpleasant scent. ~ /* #7738 */
  IF ~  NearbyDialog("DGrace")
~ THEN REPLY ~"I said, I would speak with you."~ /* #7739 */ GOTO 8
  IF ~  NearbyDialog("DAnnah")
!NearbyDialog("DGrace")
~ THEN REPLY ~"I said, I would speak with you."~ /* #7740 */ GOTO 7
  IF ~~ THEN REPLY ~Leave the creature alone.~ /* #7741 */ EXIT
END

IF ~~ THEN BEGIN 7 // from: 6.1
  SAY ~The creature's eyes focus on Annah, then narrow to slits. It opens its mouth, displaying a row of blackened fangs as fire begins to dance around the shoulders and arms of the creature. The heat emanating from it begins to rise.~ /* #7742 */
  IF ~~ THEN REPLY ~"Hey! I'm talking to you!"~ /* #7743 */ GOTO 9
  IF ~~ THEN REPLY ~Leave the creature alone, take Annah and leave.~ /* #7744 */ EXIT
END

IF ~~ THEN BEGIN 8 // from: 6.0
  SAY ~The creature's eyes focus on Fall-from-Grace, then narrow to slits. It opens its mouth, displaying a row of blackened fangs as fire begins to dance around the shoulders and arms of the creature. The heat emanating from it begins to rise.~ /* #7745 */
  IF ~~ THEN REPLY ~"Hey! I'm talking to you!"~ /* #7746 */ GOTO 10
  IF ~~ THEN REPLY ~Back away, taking Fall-from-Grace with you and leave.~ /* #7747 */ EXIT
END

IF ~~ THEN BEGIN 9 // from: 7.0
  SAY ~The creature roars, then it launches itself at Annah!~ /* #7748 */
  IF ~~ THEN REPLY ~"Dammit...!"~ /* #7749 */ DO ~Enemy()
Attack("Annah")
~ EXIT
END

IF ~~ THEN BEGIN 10 // from: 8.0
  SAY ~The creature roars, then it launches itself at Fall-from-Grace!~ /* #7750 */
  IF ~~ THEN REPLY ~"Dammit...!"~ /* #7751 */ DO ~Enemy()
Attack("Grace")
~ EXIT
END

IF ~  Global("Know_Abishai","GLOBAL",1)
~ THEN BEGIN 11 // from:
  SAY ~This black-scaled fiend towers to a height of eight feet - its great height, however, is offset by its thin, snake-like frame. A long prehensile tail drags behind it, and its leathery wings are hooked behind its back. A strong vinegary smell emanates from the fiend... as well as a certain amount of heat. It seems to be ignoring you.~ /* #7752 */
  IF ~~ THEN REPLY ~"Greetings."~ /* #7753 */ GOTO 1
  IF ~~ THEN REPLY ~Leave the abishai alone.~ /* #7758 */ EXIT
END