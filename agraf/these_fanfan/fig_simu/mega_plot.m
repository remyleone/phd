%% Load Color Chart
run('ColorChart');

%% Default value

feuille='Feuil1';
feuilleincert='Incertitude';
feuillecond = 'cond';
displaycond = true;
displayadm = true;
displayresist = true;
myplot=@plot;
ligne_offset=4;
ligne_offset_cond = 4;
figsize=[100 100 700 550]; % 600/450
voting_systems_banned = {''};

%% Universal Legend
markers=containers.Map;
colors=containers.Map;
% vs={'Majority Judgment','Approval','Range voting with average',...
%     'Borda','Veto','Plurality',...
%     'Maximin','Schulze','Baldwin','Ranked Pairs',...
%     'Nanson','Kemeny','Condorcet Sum Defeats',...
%     'VTB-Condorcet IRV','IRV','Exhaustive Ballot','IRV Duels',...
%     'Absolute-Condorcet IRV','ICRV',...
%     'Iterated Bucklin','Bucklin','Coombs','Two Round', ...
%     'not_exists_condorcet_admissible','not_exists_condorcet_winner'...
%     'not_exists_resistant_condorcet_winner'};
% m = {...
%     ... % Cardinaux
%     'd:','d--','d-'...
%     ... % RPS
%     'o-','o:','o-.',...
%     ... % Condorcet
%     '+-','+--','+-.','+:',...
%     'x-','x--','x:'...
%     ... % VTI-like: OK
%     ':','-','--','-.',...
%     ':','-.',...
%     ... % Divers
%     'x-','x:','x-.','x--',...
%     ... % Taux de Condorcet et assimilés: OK
%     '^:','^--','v-'};
% col = {...
%     ... % Cardinaux
%     DarkRed,Red,IndianRed,...
%     ... % RPS
%     Purple,Purple,Purple...
%     ... % Condorcet % **Blue, **MidnightBlue, NavyBlue, **CadetBlue, TealBlue, **Cerulean, Cyan
%     Cerulean,CadetBlue,RoyalBlue,Blue,...
%     Thistle,Purple,Blue,...
%     ... % VTI-like
%     ... % OliveGreen,LimeGreen,OliveGreen,OliveGreen,... 
%     DarkOliveGreen,LimeGreen,OliveGreen,DarkOliveGreen,... % OliveGreen, PineGreen, SpringGreen, 
%     OliveGreen,OliveGreen,...
%     ... % Divers
%     YellowOrange,YellowOrange,YellowOrange,YellowOrange,...
%     ... % Taux de Condorcet et assimilés
%     RawSienna,Brown,Sepia};
% for i=1:length(vs)
%     markers(vs{i})=m{i};
%     colors(vs{i})=col{i};
% end


% Styles autorisés : - (solid) : (dotted) -. (dashdot) -- (dashed) 
% Cardinaux
% markers('Majority Judgment') = 'd:';
% colors('Majority Judgment') = DarkRed;
% markers('Approval') = 'd--';
% colors('Approval') = Red;
% markers('Range voting with average') = 'd-';
% colors('Range voting with average') = IndianRed;
markers('Approval') = 'd-';
colors('Approval') = OrangeRed;
markers('Range voting with average') = 'd:';
colors('Range voting with average') = Crimson;
markers('Majority Judgment') = 'd--';
colors('Majority Judgment') = Red;
% RPS
% markers('Borda') = 'o-';
% colors('Borda') = Purple;
% markers('Veto') = 'o:';
% colors('Veto') = Purple;
% markers('Plurality') = 'o-.';
% colors('Plurality') = Purple;
markers('Borda') = 'o-';
colors('Borda') = Lime;
markers('Veto') = 'o:';
colors('Veto') = OliveDrab;
markers('Plurality') = 'o--';
colors('Plurality') = DarkGreen;
% Condorcet
% Group 1
markers('Condorcet Sum Defeats') = '+-.';
colors('Condorcet Sum Defeats') = BurlyWood;
markers('Kemeny') = 'x--';
colors('Kemeny') = Chocolate;
% Group 1 bis
markers('Nanson') = '+:';
colors('Nanson') = RawSienna;
% Group 2
markers('Maximin') = 'x-';
colors('Maximin') = SandyBrown;
markers('Schulze') = '+--';
colors('Schulze') = DarkGoldenrod;
markers('Ranked Pairs') = 'x:';
colors('Ranked Pairs') = SaddleBrown;
% Group 3
markers('Baldwin') = 'x-.'; % Good
colors('Baldwin') = SaddleBrown;
% IRV Family
markers('IRV Duels') = '-.';
colors('IRV Duels') = Blue;
markers('Exhaustive Ballot') = '--';
colors('Exhaustive Ballot') = Blue;
markers('IRV') = '-';
colors('IRV') = PowderBlue;
markers('VTB-Condorcet IRV') = ':';
colors('VTB-Condorcet IRV') = MidnightBlue;
% IRV Family: banned voting systems
markers('Absolute-Condorcet IRV') = ':';
colors('Absolute-Condorcet IRV') = MidnightBlue;
markers('ICRV') = '-.';
colors('ICRV') = PowderBlue;
% Misc voting systems
% markers('Iterated Bucklin') = 'x-';
% colors('Iterated Bucklin') = YellowOrange;
% markers('Bucklin') = 'x:';
% colors('Bucklin') = YellowOrange;
% markers('Coombs') = 'x-.';
% colors('Coombs') = YellowOrange;
% markers('Two Round') = 'x--';
% colors('Two Round') = YellowOrange;
markers('Coombs') = '.--';
colors('Coombs') = MediumOrchid;
markers('Iterated Bucklin') = '.-';
colors('Iterated Bucklin') = Thistle;
markers('Bucklin') = '.:';
colors('Bucklin') = DarkViolet;
markers('Two Round') = '.-.';
colors('Two Round') = Fuchsia;
% Condorcet rates
markers('not_exists_resistant_condorcet_winner') = 'v-';
colors('not_exists_resistant_condorcet_winner') = Black;
markers('not_exists_condorcet_winner') = '^:';
colors('not_exists_condorcet_winner') = Black;
markers('not_exists_condorcet_admissible') = '^--';
colors('not_exists_condorcet_admissible') = Black;


% VMF Concentration % Remettre double pourcent

xlsname='Results_2014-11-16_13-23-13_m_fr_VMF_concentration.xls';
fname='vmfconcentration';
xl='Concentration \kappa';
yl='CM rate';
x_ticks = 2.^(-3:3);
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southwest';
xsize=13;
myplot=@semilogx;

run('plotmaker')
myplot=@plot;

%% SphereC

xlsname='Results_2014-11-14_m_fr_sphere_C.xls';
fname='spherec';
xl='Number of candidates C';
yl='CM rate';
x_ticks = [3:15];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;

run('plotmaker')

%% SphereC relatif aux adm

xlsname='Results_2014-11-14_m_fr_sphere_C_copy.xls';
fname='spherec_sur_adm';
xl='Number of candidates C';
yl='CM rate';
x_ticks = [3:15];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = false;
loc='southeast';
xsize=13;

run('plotmaker')

%% Sphere V big

xlsname='Results_2014-11-14_22-54-39_m_fr_sphere_V_copy.xls';
fname='spherevbig';
xl='Number of voters V';
yl='CM rate';
x_ticks = 2.^[0:12]+1;
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@semilogx;

run('plotmaker')

% myplot=@plot;

%% Sphere V small

xlsname='Results_2014-11-14_22-54-39_m_fr_sphere_V.xls';
fname='spherevsmall';
xl='Number of voters V';
yl='CM rate';
x_ticks = [3:2:33];
x_ticks_labels = to_french(x_ticks);

displaycond = true;
displayadm = true;
loc='southeast';
xsize=31;
myplot=@plot;

run('plotmaker')

%% Sphere V small restricted

xlsname='Results_2014-11-14_22-54-39_m_fr_sphere_V.xls';
fname='spherevsmallrestricted';
xl='Number of voters V';
yl='CM rate';
x_ticks = [3:2:33];
x_ticks_labels = to_french(x_ticks);

voting_systems_banned = ...
    {'Coombs', 'Range voting with average', 'Borda', 'Approval',...
    'Plurality', 'Veto', 'Kemeny', 'Maximin', 'Schulze', 'Nanson',...
    'Ranked Pairs', 'IRV Duels', 'Two Round'};

displaycond = true;
displayadm = true;
loc='southeast';
xsize=31;
myplot=@plot;

run('plotmaker')
voting_systems_banned = {}

%% VMF Position of pole

xlsname='Results_2014-11-14_23-33-34_m_fr_VMF_position_pole.xls';
fname='vmfpoleposition';
xl='Relative position of the pole  \theta / \theta_{max}';
yl='CM rate';
x_ticks = [0:3:12];
bli = [0:0.25:1]
x_ticks_labels = to_french(bli);

displaycond = false;
displayadm = true;
loc='northwest';
xsize=13;
myplot=@plot;

run('plotmaker')

%% VMF Position of pole (hate)

xlsname='Results_2015-06-29_11-33-34_m_fr_VMF_position_pole_hate.xls';
fname='vmfpolepositionhate';
xl='Relative position of the pole \theta'' / \theta''_{max}';
yl='CM rate';
x_ticks = [0:3:12];
bli = [0:0.25:1]
x_ticks_labels = to_french(bli);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@plot;

run('plotmaker')

%% VMF Position of pole (full)

xlsname='Results_2015-06-29_11-33-34_m_fr_VMF_position_pole_full.xls';
fname='vmfpolepositionfull';
xl='Curvilinear abscissa t';
yl='CM rate';
x_ticks = [0:0.25:1];
x_ticks_labels = to_french(bli);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=25;
myplot=@plot;

run('plotmaker')

%% VMF number of poles

xlsname='Results_2014-11-16_13-25-08_m_fr_VMF_number_of_poles.xls';
fname='vmfnumberpole';
xl='Number of poles k';
yl='CM rate';
x_ticks = [1:16];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=16;
myplot=@plot;

run('plotmaker')

%% VMF angle

xlsname='Results_2014-11-17_22-36-52_m_fr_VMF_angle_between_poles.xls';
fname='vmfangle';
xl='Relative angle between the poles \theta / \theta_{max}';
yl='CM rate';
x_ticks = [0:3:12];
bli = [0:0.25:1]
x_ticks_labels = to_french(bli);

displaycond = false;
displayadm = true;
loc='northwest';
xsize=13;
myplot=@plot;

run('plotmaker')

%% GaussianC

xlsname='Results_2014-11-14_m_fr_gaussian1d_C.xls';
fname='gaussianc';
xl='Number of candidates C';
yl='CM rate';
x_ticks = [3:15];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@plot;

run('plotmaker')

%% GaussianCrestricted

xlsname='Results_2014-11-14_m_fr_gaussian1d_C.xls';
fname='gaussiancrestricted';
xl='Number of candidates C';
yl='CM rate';
x_ticks = [3:15];
x_ticks_labels = to_french(x_ticks);
voting_systems_banned = ...
    {'Condorcet Sum Defeats', 'Iterated Bucklin', 'ICRV', 'IRV Duels', ...
     'Ranked Pairs', 'Kemeny', ...
     'Maximin', 'Schulze', 'Nanson', 'Baldwin'...
    };

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@plot;

run('plotmaker')
voting_systems_banned = {};

%% GaussianC

xlsname='Results_2014-11-14_m_fr_gaussian1d_C_TM.xls';
fname='gaussianc-tm';
xl='Number of candidates C';
yl='Taux de MT';
x_ticks = [3:15];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@plot;

run('plotmaker')

%% Gaussian1d V big

xlsname='Results_2014-11-14_22-03-02_m_fr_gaussian1d_V_copy.xls';
fname='gaussian1dvbig';
xl='Number of voters V';
yl='CM rate';
x_ticks = 2.^[0:12]+1;
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='northeast';
xsize=18;
myplot=@semilogx;

run('plotmaker')
myplot=@plot;

%% Gaussian1d V small

xlsname='Results_2014-11-14_22-03-02_m_fr_gaussian1d_V.xls';
fname='gaussian1dvsmall';
xl='Number of voters V';
yl='CM rate';
x_ticks = [3:2:33];
x_ticks_labels = to_french(x_ticks);

displaycond = true;
displayadm = true;
loc='northeast';
xsize=31;
myplot=@plot;

run('plotmaker')

%% Gaussian 1D shift

xlsname='Results_2014-11-16_13-16-36_m_fr_gaussian1d_shift.xls';
fname='gaussian1dshift';
xl='Shift y_0';
yl='CM rate';
x_ticks = [0:0.2:2];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='northeast';
xsize=11;
myplot=@plot;

run('plotmaker')

%% Gaussian XD

xlsname='Results_2014-11-14_22-32-35_m_fr_gaussian_xd.xls';
fname='gaussianxd';
xl='Number of dimensions d';
yl='CM rate';
x_ticks = [0:10];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='northeast';
xsize=10;
myplot=@plot;

run('plotmaker')

%% Gaussian 2D

xlsname='Results_2014-11-16_13-18-07_m_fr_gaussian2d_ratio.xls';
fname='gaussian2d';
xl='Standard deviation along second dimension \sigma_2';
yl='CM rate';
x_ticks = [0:0.1:1];
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='northeast';
xsize=11;
myplot=@plot;

run('plotmaker')

%% Euclidian V big

xlsname='Results_2014-11-14_22-33-28_m_fr_euclidean1d_V_copy.xls';
fname='euclidianvbig';
xl='Number of voters V';
yl='CM rate';
x_ticks = 2.^[0:12]+1;
x_ticks_labels = to_french(x_ticks);

displaycond = false;
displayadm = true;
loc='southeast';
xsize=13;
myplot=@semilogx;

run('plotmaker')
myplot=@plot;

%% Euclidian V small

xlsname='Results_2014-11-14_22-33-28_m_fr_euclidean1d_V.xls';
fname='euclidianvsmall';
xl='Number of voters V';
yl='CM rate';
x_ticks = [3:2:33];
x_ticks_labels = to_french(x_ticks);

displaycond = true;
displayadm = true;
loc='southeast';
xsize=31;
myplot=@plot;

run('plotmaker')




