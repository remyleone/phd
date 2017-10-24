function tutu = to_french(toto)
    tutu = {};
    for i = [1:length(toto)]
        tutu = horzcat(tutu, strrep(num2str(toto(i)), '.', ','));
    end