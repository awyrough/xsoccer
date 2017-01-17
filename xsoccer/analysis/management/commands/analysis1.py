import datetime
import csv
import os
import time

from django.core.management.base import BaseCommand, CommandError
from eventstatistics.models import EventStatistic
from games.models import Game
from lineups.models import Lineup
from players.models import Player
from playerstatistics.models import PlayerStatistic
from salaries.models import Salary
from statistictypes.models import StatisticType
from teams.models import Team
from teamstatistics.models import TeamStatistic
from venues.models import Venue


class Command(BaseCommand):
	help = 'Pull the statistics of a team across a time-range; classify by outcome'

	def add_arguments(self,parser):
		# add optional print to csv flag
		parser.add_argument(
			"--team_uuid",
            dest="team_uuid",
            default="",
            help="Desried Opta team ID",
            )
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
		parser.add_argument(
			"--startdate",
            dest="startdate",
            default='1900-01-01',
            help="Example format: 1900-01-31",
            )
		parser.add_argument(
			"--enddate",
            dest="enddate",
            default='2900-01-01',
            help="Example format: 1900-01-31",
            )
	def handle(self,*args,**options):
		#handle import parameters
		if not options["team_uuid"]:
			raise Exception("Opta team ID is needed")
		is_print_to_csv = options["print_to_csv"]
		arg_team_uuid = str(options["team_uuid"])
		arg_startdate = str(options["startdate"])
		arg_enddate = str(options["enddate"])
		
		arg_startdate = datetime.datetime.strptime(arg_startdate, "%Y-%m-%d")
		arg_enddate = datetime.datetime.strptime(arg_enddate, "%Y-%m-%d")

		#load team
		db_team = Team.objects.get(uuid=arg_team_uuid)

		#brute force selecting all possible stats; 
		all_stats_to_consider = [
			"accurate_back_zone_pass"
			,"accurate_corners_intobox"
			,"accurate_cross"
			,"accurate_cross_nocorner"
			,"accurate_fwd_zone_pass"
			,"accurate_goal_kicks"
			,"accurate_keeper_throws"
			,"accurate_launches"
			,"accurate_layoffs"
			,"accurate_long_balls"
			,"accurate_pass"
			,"accurate_through_ball"
			,"accurate_throws"
			,"aerial_lost"
			,"aerial_won"
			,"att_bx_centre"
			,"att_obx_centre"
			,"att_corner"
			,"att_fastbreak"
			,"att_freekick_goal"
			,"att_freekick_target"
			,"att_freekick_total"
			,"att_goal_high_centre"
			,"att_goal_high_left"
			,"att_goal_high_right"
			,"att_goal_low_centre"
			,"att_goal_low_left"
			,"att_goal_low_right"
			,"att_hd_goal"
			,"att_hd_miss"
			,"att_hd_post"
			,"att_hd_target"
			,"att_hd_total"
			,"att_ibox_blocked"
			,"att_ibox_goal"
			,"att_ibox_miss"
			,"att_ibox_post"
			,"att_ibox_target"
			,"att_ibox_own_goal"
			,"att_obox_own_goal"
			,"att_lf_goal"
			,"att_lf_target"
			,"att_lf_total"
			,"att_miss_high"
			,"att_miss_high_left"
			,"att_miss_high_right"
			,"att_miss_left"
			,"att_miss_right"
			,"att_obox_blocked"
			,"att_obox_goal"
			,"att_obox_miss"
			,"att_obox_post"
			,"att_obox_target"
			,"att_obp_goal"
			,"att_one_on_one"
			,"att_openplay"
			,"att_pen_goal"
			,"att_pen_miss"
			,"att_pen_post"
			,"att_pen_target"
			,"att_post_high"
			,"att_post_left"
			,"att_post_right"
			,"att_rf_goal"
			,"att_rf_target"
			,"att_rf_total"
			,"att_setpiece"
			,"att_sv_high_centre"
			,"att_sv_high_left"
			,"att_sv_high_right"
			,"att_sv_low_centre"
			,"att_sv_low_left"
			,"att_sv_low_right"
			,"attempts_conceded_ibox"
			,"attempts_conceded_obox"
			,"back_pass"
			,"ball_recovery"
			,"blocked_scoring_att"
			,"challenge_lost"
			,"clean_sheet"
			,"clearance_off_line"
			,"contentious_decision"
			,"corner_taken"
			,"cross_not_claimed"
			,"crosses_18yard"
			,"crosses_18yardplus"
			,"dangerous_play"
			,"defender_goals"
			,"dispossessed"
			,"dive_catch"
			,"dive_save"
			,"duel_lost"
			,"duel_won"
			,"effective_clearance"
			,"effective_head_clearance"
			,"error_lead_to_goal"
			,"error_lead_to_shot"
			,"final_third_entries"
			,"fk_foul_won"
			,"fk_foul_lost"
			,"forward_goals"
			,"fouls"
			,"fouled_final_third"
			,"game_started"
			,"gk_smother"
			,"goal_assist"
			,"goal_assist_intentional"
			,"goal_kicks"
			,"goals"
			,"goals_conceded"
			,"goals_conceded_ibox"
			,"goals_conceded_obox"
			,"good_high_claim"
			,"goals_openplay"
			,"hand_ball"
			,"head_clearance"
			,"head_pass"
			,"interception"
			,"interceptions_in_box"
			,"keeper_pick_up"
			,"keeper_throws"
			,"last_man_contest"
			,"last_man_tackle"
			,"long_pass_own_to_opp"
			,"long_pass_own_to_opp_success"
			,"lost_corners"
			,"mins_played"
			,"midfielder_goals"
			,"offside_provoked"
			,"offtarget_att_assist"
			,"ontarget_att_assist"
			,"ontarget_scoring_att"
			,"outfielder_block"
			,"own_goals"
			,"passes_left"
			,"passes_right"
			,"pen_goals_conceded"
			,"penalty_conceded"
			,"penalty_save"
			,"penalty_won"
			,"possession_percentage"
			,"post_scoring_att"
			,"punches"
			,"red_card"
			,"saved_ibox"
			,"saved_obox"
			,"saved_setpiece"
			,"saves"
			,"second_yellow"
			,"second_goal_assist"
			,"shot_off_target"
			,"six_second_violation"
			,"six_yard_block"
			,"stand_catch"
			,"stand_save"
			,"subs_made"
			,"total_att_assist"
			,"total_back_zone_pass"
			,"total_clearance"
			,"total_contest"
			,"total_corners_intobox"
			,"total_cross"
			,"total_cross_nocorner"
			,"total_fastbreak"
			,"total_fwd_zone_pass"
			,"total_high_claim"
			,"total_launches"
			,"total_layoffs"
			,"total_long_balls"
			,"total_offside"
			,"total_pass"
			,"total_scoring_att"
			,"total_sub_off"
			,"total_sub_on"
			,"total_tackle"
			,"total_through_ball"
			,"total_throws"
			,"total_yel_card"
			,"total_red_card"
			,"touches"
			,"turnover"
			,"was_fouled"
			,"won_contest"
			,"won_corners"
			,"won_tackle"
			,"yellow_card"
			,"total_flick_on"
			,"accurate_flick_on"
			,"total_chipped_pass"
			,"accurate_chipped_pass"
			,"blocked_cross"
			,"shield_ball_oop"
			,"foul_throw_in"
			,"effective_blocked_cross"
			,"penalty_faced"
			,"total_pull_back"
			,"accurate_pull_back"
			,"total_keeper_sweeper"
			,"accurate_keeper_sweeper"
			,"goal_assist_openplay"
			,"goal_assist_setplay"
			,"att_assist_openplay"
			,"att_assist_setplay"
			,"overrun"
			,"interception_won"
			,"big_chance_created"
			,"big_chance_missed"
			,"big_chance_scored"
			,"unsuccessful_touch"
			,"fwd_pass"
			,"backward_pass"
			,"leftside_pass"
			,"rightside_pass"
			,"successful_final_third_passes"
			,"total_final_third_passes"
			,"rescinded_red_card"
			,"diving_save"
			,"poss_won_def_3rd"
			,"poss_won_mid_3rd"
			,"poss_won_att_3rd"
			,"poss_lost_all"
			,"poss_lost_ctrl"
			,"goal_fastbreak"
			,"shot_fastbreak"
			,"pen_area_entries"
			,"final_third_entry"
			,"hit_woodwork"
			,"goal_assist_deadball"
			,"freekick_cross"
			,"accurate_freekick_cross"
			,"open_play_pass"
			,"successful_open_play_pass"
			,"attempted_tackle_foul"
			,"fifty_fifty"
			,"successful_fifty_fifty"
			,"blocked_pass"
			,"failed_to_block"
			,"put_through"
			,"successful_put_through"
			,"assist_pass_lost"
			,"assist_blocked_shot"
			,"assist_attempt_saved"
			,"assist_post"
			,"assist_free_kick_won"
			,"assist_handball_won"
			,"assist_own_goal"
			,"assist_penalty_won"
			,"shots_conc_onfield"
			,"goals_conc_onfield"
			,"pts_dropped_winning_pos"
			,"pts_gained_losing_pos"
			,"touches_in_opp_box"
			,"att_bx_right"
			,"att_bx_left"
			,"att_cmiss_high"
			,"att_cmiss_high_left"
			,"att_cmiss_high_right"
			,"att_cmiss_left"
			,"att_cmiss_right"
			,"att_obxd_right"
			,"att_freekick_miss"
			,"att_obx_right"
			,"att_obx_left"
			,"att_lg_centre"
			,"att_obxd_left"
			,"att_freekick_post"
			,"att_lg_right"
			,"att_lg_left"
			,"formation_used"
			,"first_half_goals"
			,"own_goal_accrued"
			]


		print "Analyzing %s Stats for %s between %s and %s" % \
					(
						len(all_stats_to_consider)
						,db_team
						,arg_startdate
						,arg_enddate
					)
 
		if is_print_to_csv:	
			os.chdir("/Users/Swoboda/Desktop/")

			output_filename = "twosamp_results__" + str(time.strftime('%Y_%m_%d')) + "_" + arg_filename + ".csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")

			writer.writerow(header)
		
			for r in results:
				writer.writerow(r)

			output.close()	