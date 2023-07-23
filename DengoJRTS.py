# -*- coding: utf-8 -*-
################################################################################
# Den-Go controller "One Handle MasCon for Nintendo Switch"
#
#	usage : python DengoJRTS.py
#
#	F.S.Enterprise
#
#	History
#		Rev 1.0:2023-02-25
#		Rev 1.1:2023-03-04
#		Rev	1.2:2023-05-07
#		Rev 1.3:2023-07-23
#
from pygame.locals import *
import pygame
import keyboard
import sys


#	キーボードでの操作
#
#		・1ハンドル車（E233系など）の運転
#			非常ブレーキ						「 1 」
#			ブレーキを強める／加速を弱める		「 Q 」
#			ブレーキ・加速ゼロ（惰性で走る）	「 S 」
#			ブレーキを弱める／加速を強める		「 Z 」
#
#		・2ハンドル車（211系など）の運転
#			非常ブレーキ						「 / 」
#			ブレーキを強める					「 . 」
#			ブレーキを弱める					「 , 」
#			ブレーキゼロ						「 M 」
#			加速を強める						「 Z 」
#			加速を弱める						「 A 」
#			加速ゼロ							「 S 」
#
#		・そのほかの操作 ※操作する機器が設置されていない車種の場合は動作しません。
#			運転台表示／非表示					「 C 」
#			運転情報表示（HUD）表示／非表示		「 V 」
#			ポーズ（一時停止）					「 Esc 」
#			レバーサ（逆転器） 前／後 			「 ↑ 」／「 ↓ 」
#			EBリセットスイッチ					 E 」
#			警笛（1段目）						「 Enter 」／「 BackSpace 」
#			警笛（2段目） 						「 BackSpace 」 ※2段目がある車両のみ
#			ATS確認ボタン 						「 Space 」
#			警報持続ボタン						「 X 」
#			ATS復帰スイッチ（常用） 			「 Y 」
#			ATS復帰スイッチ（非常）				「 U 」
#			連絡ブザー							「 B 」
#			インチングボタン					「 I 」
#			定速/抑速（抑速2）スイッチ			「 W 」
#			抑速1スイッチ 						「 D 」
#			勾配起動ボタン 						「 K 」
#			TASC切スイッチ						「 T 」
#

########################################
# MasCon Analog Value			Button and Hat Switch
#
#	-1.0						y		0
#	-0.9609375              	b		1
#	-0.8515625              	a		2
#	-0.75                   	x		3
#	-0.640625               	L		4
#	-0.53125                	R		5
#	-0.4296875              	ZL		6
#	-0.3203125              	ZR		7
#	-0.2109375              	-		8
#	0.0                     	+		9
#	0.23809814453125        	home	12
#	0.4285888671875         	○		13
#	0.611114501953125			↑		0, 1
#	0.80157470703125           	←		-1, 0
#	0.999969482421875          	→		1, 0
#                              	↓		0, -1
#
#	Layout
#
#			ZL			ZR
#		ZR		-	+		R
#
#				○	home
#
#			↑			X
#		←		→	Y		A
#			↓			B
#

########################################
#
MajorRevision		= 1
MinorRevision		= 3
MaxJoystickNum		= 10
JoystickName		= "One Handle MasCon for Nintendo Switch"
MasConPos			= (	-1.00,	# EB
						-0.96,	# B8
						-0.85,	# B7
						-0.75,	# B6
						-0.64,	# B5
						-0.53,	# B4
						-0.42,	# B3
						-0.32,	# B2
						-0.21,	# B1
						 0.00,	# N
						 0.23,	# P1
						 0.42,	# P2
						 0.61,	# P3
						 0.80,	# P4
						 0.99	# P5
					)
MasConText			= ('EB', 'B8', 'B7', 'B6', 'B5', 'B4', 'B3', 'B2', 'B1', 'N', 'P1', 'P2', 'P3', 'P4', 'P5', )
MasConNPos			= 9
MasConAxisNum		= 1
HatNum				= 0
ButtonMap			= (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13)
ButtonText			= ('SW_Y' ,'SW_B', 'SW_A', 'SW_X', 'SW_L', 'SW_R', 'SW_ZL', 'SW_ZR', 'SW_-', 'SW_+', 'SW_HOME', 'SW_CIRCLE')
InitialMasConPos	= 3
BrakeLimit211		= 1
Train211			= '211'
TrainE233			= 'E233'

bDebug				= False

########################################
# Den-Go controller class
#
class dengo():

	####################################
	# Constoructor
	#
	def __init__(self):
		self.InitializeParameters()

	####################################
	# Change Train Control
	#
	def SetTrain(self, train):
		self.TrainType = train
		print('Train ' + train + ' Selected.')

	####################################
	# Return Train was 211
	#
	def IsTrain211(self):
		return (self.TrainType == Train211)

	####################################
	# Return Train was E233
	#
	def IsTrainE233(self):
		return (self.TrainType == TrainE233)

	####################################
	# Parameter Initializer
	#
	def InitializeParameters(self):
		#
		self.CurrentMasConIndex = InitialMasConPos
		self.LastMasConIndex    = InitialMasConPos
		self.CurrentHatState    = [0, 0]
		self.LastHatState       = [0, 0]
		self.BreakStep          = 0
		self.AccelStep          = 0
		self.ButtonQueue        = []
		self.TrainType			= Train211
		self.ButtonState        = [False, False, False, False, False, False, False, False, False, False, False, False]

	####################################
	# Control Initializer
	#
	#	Flase : No controller
	#
	def InitializeControls(self):

		################################
		# Check for Available Joystick
		#
		try:
			# check Joystick count
			#
			num = pygame.joystick.get_count()
			if num == 0:
				raise pygame.error

			# check joystick name
			#
			print('[Check Available Joystick(s)]')
			print(' ' + str(num) + ' Joystick(s) Available.')
			print(' Trying to find Controller ....', end = ' ')
			for i in range(num):
				self.joy = pygame.joystick.Joystick(i)
				self.joy.init()
				if self.joy.get_name() == JoystickName:
					print('Found.')
					print(' Device Name "' + self.joy.get_name() + '" as Joystick Number ' + str(i) + '.')
					print('')
					break

		#
		except pygame.error:
			return False, 'No Joystick.'

		################################
		# Check Buttons, Axis and Hats available
		#
		try:
			#
			print('[Available Control Information]')
			print(" Number of Buttons : " + str(self.joy.get_numbuttons()))
			print(" Number of Axes    : " + str(self.joy.get_numaxes()))
			print(" Number of Hats    : " + str(self.joy.get_numhats()))
			print('')

		#
		except pygame.error:
			return False, 'No Joystick.'

		################################
		# Check for Available Buttons
		#
		try:
			#
			print('[Check Available Buttons]')
			print(' ', end = ' ')
			for i in ButtonMap:
				self.joy.get_button(i)
				print(str(i), end = ' ')

			print('Available.')
			print('')

		#
		except pygame.error:
			return False, 'Button Map Error.'

		################################
		# Check for Available Axis
		#
		try:
			# One Handle Controller use as MasConAxisNum(1)
			#
			print('[Check Available Axis]')
			self.joy.get_axis(MasConAxisNum)
			print(' MasCon Number ' + str(MasConAxisNum) + ' Available.')
			print('')

		#
		except pygame.error:
			s = 'Axis must be' + str(MasConAxisNum)
			return False, s

		################################
		# Check fot Hat Existence
		#
		try:
			#
			print('[Check Available Hat]')
			self.joy.get_hat(HatNum)
			print(' Hat Number ' + str(HatNum) + ' Available. (Not in Use)')
			print('')

		#
		except pygame.error:
			s = 'Hat must be' + str(HatNum)
			return False, s

		################################
		# Store Initial Status
		#
		self.UpdateAxis(False);
		self.LastMasConIndex = self.CurrentMasConIndex
		self.LastHatState    = self.CurrentHatState
		self.BreakStep       = 0
		self.AccelStep       = 0

		return True, ''

	####################################
	# Update Axis Input
	#
	#	bOutput		output gamepad key
	#
	def UpdateAxis(self, bOutput = True):

		bRet = False

		#
		self.ButtonQueue = []
		pygame.event.get()

		################################
		# Axis analog value to index
		#
		#	EB	B8	B7	B6	B5	B4	B3	B2	B1	0	P1	P2	P3	P4	P5
		#	0	1	2	3	4	5	6	7	8	9	10	11	12	13	14
		#
		#	MasConPos is array of axis value related knotch position
		#
		#
		pos  = self.joy.get_axis(MasConAxisNum)

		# i is index of <asConPos
		#
		for i in range(len(MasConPos)):

			# until last index of MasConPos
			#
			if i < len(MasConPos) - 1:

				# boundary value is center value between current and next
				#
				boundary = (MasConPos[i + 0] + MasConPos[i + 1]) / 2

			# last index of MasConPos
			#
			else:
				# no next value, virtual center value between current and next
				#	virtual next value is 0.2 offset of current
				#
				boundary = (MasConPos[i + 0] + MasConPos[i + 0] + 0.2) / 2

			# current value is under boundary means current value is between i and i + 1
			#	so index is updated by i
			#
			if pos < boundary:
				self.CurrentMasConIndex = i
				break

		################################
		# Update Master Controller Status for 211
		#
		if self.IsTrain211():

#			if self.CurrentMasConIndex < BrakeLimit211:
#				self.CurrentMasConIndex = BrakeLimit211

			self._AxisToStep211()
			if bOutput:
				bRet = self._MasConAction211()

		################################
		# Update Master Controller Status for E233
		#
		elif self.IsTrainE233:
			self._AxisToStepE233()
			if bOutput:
				bRet = self._MasConActionE233()

		################################
		# Update last MasCon index
		#
		self.LastMasConIndex = self.CurrentMasConIndex

		return bRet

	####################################
	# Update Button Input
	#
	def UpdateButton(self):

		################################
		# Device Input to Button Status
		#
		for i in range(len(ButtonMap)):

			############################
			# Button pressed and buttin state is false,
			#	append button text and set button state true
			#
			if self.joy.get_button(ButtonMap[i]) and self.ButtonState[i] == False:
				self.ButtonQueue.append(ButtonText[i])
				self.ButtonState[i] = True
#				print(self.ButtonState)

			############################
			# Button released and button state is true,
			#	set button sate false
			#
			elif self.joy.get_button(ButtonMap[i]) == False and self.ButtonState[i] == True:
				self.ButtonState[i] = False
#				print(self.ButtonState)

		############################
		# Key translate for 211
		#
		if self.IsTrain211():
			self._KeyAction211()

		############################
		# Key translate for E233
		#
		elif self.IsTrainE233():
			self._KeyActionE233()

	####################################
	# Update HAT input
	#
	def UpdateHat(self):

		#
		self.CurrentHatState = self.joy.get_hat(HatNum)

		################################
		#
		for i in range(2):
			if self.LastHatState[i] != self.CurrentHatState[i]:
				print(str(i) + ':' + str(self.CurrentHatState[i]))

				########################
				# Press Hat Button
				#
				if self.CurrentHatState[i] != 0:
					pass

				########################
				# Release Hat Button
				#
				else:
					pass

		################################
		# Update last HatState
		#
		self.LastHatState = self.CurrentHatState

	####################################
	# Update Master Controller Status for 211
	#
	def _AxisToStep211(self):

		################################
		# Some thing moving detected ?
		#
		if self.LastMasConIndex != self.CurrentMasConIndex:

			idxList = [self.LastMasConIndex, self.CurrentMasConIndex]

			############################
			# Index to Accell or Brake step
			#
			#	Ccross over N position
			#
			if min(idxList) < MasConNPos and max(idxList) >= MasConNPos:

				########################
				# Access Action
				#
				#	moving before N pos to after N pos
				#
				if self.LastMasConIndex < MasConNPos:
					self.BreakStep = self.LastMasConIndex - MasConNPos
					self.AccelStep = self.CurrentMasConIndex - MasConNPos

				########################
				# Brake Action
				#
				#	moving after N pos to before N pos
				#
				else:
					self.BreakStep = MasConNPos - self.CurrentMasConIndex
					self.AccelStep = MasConNPos - self.LastMasConIndex

			############################
			# Not cross over N position
			#
			else:

				########################
				# Before N position (Only Brake area)
				#
				if self.CurrentMasConIndex < MasConNPos:
					self.BreakStep = self.LastMasConIndex - self.CurrentMasConIndex

				########################
				# After N position (Only Accel area)
				#
				if self.CurrentMasConIndex >= MasConNPos:
					self.AccelStep = self.CurrentMasConIndex - self.LastMasConIndex

#		print('Last   : ' + str(self.LastMasConIndex))
#		print('Current: ' + str(self.CurrentMasConIndex))

	####################################
	# Update Master Controller Status for 233
	#
	def _AxisToStepE233(self):

		################################
		# Some thing moving detected ?
		#
		if self.LastMasConIndex != self.CurrentMasConIndex:

			self.BreakStep = 0
			self.AccelStep = self.CurrentMasConIndex - self.LastMasConIndex

#		print('Last   : ' + str(self.LastMasConIndex))
#		print('Current: ' + str(self.CurrentMasConIndex))

	####################################
	# Make keycode for 211 accel and brake control
	#
	def _MasConAction211(self):

		################################
		# Brake step available ?
		#
		if self.BreakStep != 0:

			############################
			# Increlase Brake Action
			#
			if self.BreakStep > 0:
				while self.BreakStep > 0:
					keyboard.press_and_release(".")
					self.BreakStep = self.BreakStep - 1
					if (bDebug):
						print('.')

			############################
			# Decrease Brake Action
			#
			else:
				while self.BreakStep < 0:
					keyboard.press_and_release(",")
					self.BreakStep = self.BreakStep + 1
					if (bDebug):
						print(',')

			return True

		################################
		# Accel step available ?
		#
		if self.AccelStep != 0:

			############################
			# Increlase Accel Action
			#
			if self.AccelStep > 0:
				while self.AccelStep > 0:
					keyboard.press_and_release("z")
					self.AccelStep = self.AccelStep - 1
					if (bDebug):
						print('z')

			############################
			# Decrease Accel Action
			#
			else:
				while self.AccelStep < 0:
					keyboard.press_and_release("a")
					self.AccelStep = self.AccelStep + 1
					if (bDebug):
						print('a')

			return True

		return False

	####################################
	# Make keycode for E233 accel and brake control
	#
	def _MasConActionE233(self):

		################################
		# Accel step available ?
		#
		if self.AccelStep != 0:

			############################
			# Increlase Accel Action
			#
			if self.AccelStep > 0:
				while self.AccelStep > 0:
					keyboard.press_and_release("z")
					self.AccelStep = self.AccelStep - 1
					if (bDebug):
						print('z')

			############################
			# Decrease Accel Action
			#
			else:
				while self.AccelStep < 0:
					keyboard.press_and_release("q")
					self.AccelStep = self.AccelStep + 1
					if (bDebug):
						print('q')

			return True

		return False

	####################################
	# Key translate action for 211
	#
	def _KeyAction211(self):

		################################
		#
		for b in self.GetButtons():
#			print(b)
#			print(type(b))

			############################
			# Cut off TASC
			#
			if b == 'SW_Y':
				keyboard.press_and_release("t")
				if (bDebug):
					print('t')

			############################
			# Change Train to E233
			#
			elif b == 'SW_B':
				self.SetTrain(TrainE233)

			############################
			# Change Train to 211
			#
			elif b == 'SW_A':
				self.SetTrain(Train211)

			############################
			# Change Console
			#
			elif b == 'SW_X':
				keyboard.press_and_release("c")
				if (bDebug):
					print('c')

			elif b == 'SW_L':
				pass

			############################
			# Continue Alarm
			#
			elif b == 'SW_R':
				keyboard.press_and_release("x")
				if (bDebug):
					print('x')

			############################
			# Emergency Brake (EB)
			#	manual shows use '/' for 211, but '1' is better
			#
			elif b == 'SW_ZL':
				keyboard.press_and_release("1")
				if (bDebug):
					print('1')

			############################
			# ATS Check
			#
			elif b == 'SW_ZR':
				keyboard.press_and_release(" ")
				print(' ')

			elif b == 'SW_-':
				pass
			elif b == 'SW_+':
				pass
			elif b == 'SW_HOME':
				pass
			elif b == 'SW_CIRCLE':
				pass

	####################################
	# Key translate action for E233
	#
	def _KeyActionE233(self):
		for b in self.GetButtons():

			############################
			# Cut off TASC
			#
			if b == 'SW_Y':
				keyboard.press_and_release("t")
				if (bDebug):
					print('t')

			############################
			# Change Train to E233
			#
			elif b == 'SW_B':
				self.SetTrain(TrainE233)

			############################
			# Change Train to 211
			#
			elif b == 'SW_A':
				self.SetTrain(Train211)

			############################
			# Change Console
			#
			elif b == 'SW_X':
				keyboard.press_and_release("c")
				if (bDebug):
					print('c')

			elif b == 'SW_L':
				pass

			############################
			# Continue Alarm
			#
			elif b == 'SW_R':
				keyboard.press_and_release("x")
				if (bDebug):
					print('x')

			############################
			# Emergency Brake (EB)
			#
			elif b == 'SW_ZL':
				keyboard.press_and_release("1")
				if (bDebug):
					print('1')

			############################
			# ATS Check
			#
			elif b == 'SW_ZR':
				keyboard.press_and_release(" ")
				print(' ')

			elif b == 'SW_-':
				pass
			elif b == 'SW_+':
				pass
			elif b == 'SW_HOME':
				pass
			elif b == 'SW_CIRCLE':
				pass

	####################################
	#
	def GetMasConKnotch(self):
		return self.CurrentMasConIndex

	####################################
	#
	def GetMasConKnotchText(self):
		return MasConText[self.CurrentMasConIndex]

	####################################
	#
	def GetButtons(self):
		return self.ButtonQueue

########################################
# main program
#
def main():
	print('-----------------------------------------------')
	print('--- Input Converter for JRE Train Simulator ---')
	print('--- [One Handle MasCon for Nintendo Switch] ---')
	print('---                          F.S.Enterprise ---')
	print('---                          Revision ' + str(MajorRevision) + '.' + str(MinorRevision) + '   ---')
	print('---                                         ---')
	print('---   Button Map                            ---')
	print('---     ZL   Emergency Brake (EB)           ---')
	print('---     ZR   ATS Check                      ---')
	print('---     A    Train 211                      ---')
	print('---     B    Train E233                     ---')
	print('---     home Quit                           ---')
	print('---     X    Change Console                 ---')
	print('---     Y    Cut off TASC                   ---')
	print('---     L    n/a                            ---')
	print('---     R    Continue Alarm                 ---')
	print('---     -    n/a                            ---')
	print('---     +    n/a                            ---')
	print('---     ○    n/a                            ---')
	print('---     ↑    n/a                            ---')
	print('---     ←    n/a                            ---')
	print('---     →    n/a                            ---')
	print('---     ↓    n/a                            ---')
	print('-----------------------------------------------')
	print('')

	####################################
	# pygame initialize screen
	#
	pygame.init()
#	screen = pygame.display.set_mode((640, 480))
#	pygame.display.set_caption("Den-Go Converter")
#	screen.fill((0, 0, 0)) 

	####################################
	# create Den-Go object and Initialize
	#
	den = dengo()
	print('Initializing ...')
	print('')
	ret, text = den.InitializeControls()

	####################################
	# Initilize Succeeded ?
	#
	if ret:
		print('Initialize Succeeded.')
		cont = True

		################################
		# defauld train 211
		#
		den.SetTrain(Train211)

		################################
		#
		while True:

			############################
			# after window closed, quit app
			#
#			for event in pygame.event.get():
#				if event.type == QUIT:
#					pygame.quit()
#					sys.exit()

			############################
			#
			if (den.UpdateAxis()):
				print(den.GetMasConKnotchText())
#			print(den.GetButtons())

			den.UpdateButton()
			den.UpdateHat()

			############################
			# home button is for quit qction
			#
			for b in den.GetButtons():
#				print(b)
#				print(type(b))
				if b == 'SW_HOME':
					print('Exit.')
					pygame.quit()
					sys.exit()

#			pygame.event.pump() #おまじない
#			key = pygame.key.get_pressed()
#			print(key[pygame.K_HOME])
#			if key[pygame.K_HOME] == 1:
#				print('Exit.')
#				pygame.quit()
#				sys.exit()

#			pygame.display.update()

	####################################
	# Initilize Faild
	#
	else:
		print(text)
		print('Error occured, check the device.')

################################################################################
if __name__ == "__main__":
	main()
