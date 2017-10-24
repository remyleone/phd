%%
run('ColorChart');

markers=containers.Map;
colors=containers.Map;

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

%%
feuille='Feuil1';
myplot=@plot;
ligne_offset=4;
figsize=[100 100 700 550]; % 600/450
voting_systems_banned = {...
    'Approval','Bucklin','Coombs','Exhaustive Ballot',...
    'Majority Judgment','Plurality','Range voting with average',...
    'Two Round','Veto','Borda',...
    'Maximin','Absolute-Condorcet IRV','IRV','VTB-Condorcet IRV',...
    'Schulze','irv duels'};
xlsname='Results_2014-11-14_m_fr_sphere_C_perf_algos.xls';
fname='perf_generic_algos';
xl='C';
yl='Taux de non-décision';
x_ticks = 3:15;
x_ticks_labels = to_french(x_ticks);

loc='northeast';
xsize=13;

%% Importing
courbes=containers.Map;
% Import legends / VS, assuming it is in Feuil1
[~, ~, raw] = xlsread(xlsname,feuille)
vsnames= raw(ligne_offset,2:24);
vsnames(cellfun(@(x) ~isempty(x) && isnumeric(x) && isnan(x),vsnames)) = {''};

% Import the data
datas = raw(ligne_offset+1:(xsize+ligne_offset),2:24);
datas = cell2mat(datas);
xx = raw(ligne_offset+1:(xsize+ligne_offset),1);
xx = cell2mat(xx);
% xx=xx/12;
% Clear temporary variables
clearvars raw;

% Absolute-Condorcet IRV
for i=1:length(vsnames)
    if strcmp(vsnames{i},'Absolute-Condorcet IRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end

% ICRV
for i=1:length(vsnames)
    if strcmp(vsnames{i},'ICRV')
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
        break
    end
end

% Other banned vs
lengthvs = length(vsnames)
for i=lengthvs:-1:1
    i
    vsnames{i}
    any(ismember(voting_systems_banned,vsnames{i}))
    if any(ismember(voting_systems_banned,vsnames{i}))
        vsnames=[vsnames(1:(i-1)) vsnames(i+1:end)];
        datas(:,i)=[];
    end
end

% VTB-Condorcet IRV -> Condorcet IRV

% Populate courbes
for i=1:length(vsnames)
    disp(vsnames{i})
    courbes(vsnames{i})={datas(:,i),vsnames{i},markers(vsnames{i}),colors(vsnames{i})}; % y legend marker
end

%% Creating legends
lege={};
for i=1:length(vsnames)
    switch vsnames{i}
        case 'Approval'
            toto='VA';
        case 'Baldwin'
            toto='Bald.';
        case 'Borda'
            toto='Bor.';
        case 'Bucklin'
            toto='Buck.';
        case 'Coombs'
            toto='Coo.';
        case 'Range voting with average'
            toto='VN';
        case 'VTB-Condorcet IRV'
            toto='CVTI';
        case 'Majority Judgment'
            toto='JM';
        case 'Plurality'
            toto='Uni.';
        case 'Kemeny'
            toto='Kem.';
        case 'Maximin'
            toto='Max.';
        case 'Nanson'
            toto='Nan.';
        case 'Exhaustive Ballot'
            toto='SE';
        case 'Iterated Bucklin'
            toto='BI';
        case 'Schulze'
            toto='Sch.';
        case 'Two Round'
            toto='U2T';
        case 'IRV'
            toto='VTI';
        case 'IRV Duels'
            toto='VTID';
        case 'Ranked Pairs'
            toto='PO';
        case 'Condorcet Sum Defeats'
            toto='CSD';
        case 'not_exists_condorcet_admissible'
            toto='Non Adm.';
        case 'not_exists_condorcet_winner'
            toto='Non Cond.';
        case 'not_exists_resistant_condorcet_winner'
            toto='Non Res.';
        otherwise
            toto = vsnames{i};
    end
    switch vsnames{i}
        case 'not_exists_condorcet_admissible'
            lege{i}=toto;
        case 'not_exists_condorcet_winner'
            lege{i}=toto;
        case 'not_exists_resistant_condorcet_winner'
            lege{i}=toto;
        otherwise
            lege{i}=toto;
    end
end


%% Plot
clf
h=figure(1);
for i=1:length(vsnames)
    courbe=courbes(vsnames{i}); % y legend marker
    myplot(xx,courbe{1},courbe{3},'color',courbe{4},'linewidth',1,'markersize',8)
    hold on
end
hold off
l=legend(lege,'Location',loc,'fontsize',8);
%set(h,'Location',get)
xlabel(xl)
ylabel(yl)
% Pole position trick
% tata=0:3:12;
% set(gca,'XTick',tata); % Change x-axis ticks
% set(gca,'XTickLabel',0:.25:1); % Change x-axis ticks labels to desired values.
% tata=2.^(1:10)+1;
% tata=2.^(-3:3);
set(gca,'XTick',x_ticks); % Change x-axis ticks
set(gca,'XTickLabel',x_ticks_labels); % Change x-axis ticks labels to desired values.
xlim([min(xx) max(xx)])
ylim([0 1])
y_ticks_labels = {'0 %', '10 %', '20 %', '30 %', '40 %', '50 %', ...
    '60 %', '70 %', '80 %', '90 %', '100 %'};
set(gca,'YTickLabel',y_ticks_labels);
set(gcf, 'PaperPositionMode', 'auto');
% set(gcf, 'PaperUnits', 'inches');
% set(gcf, 'PaperPosition', [.25 .25 12 8]);

set(h, 'Position', figsize)


print(h,'-depsc2',fname)
print(h,'-djpeg',fname)





