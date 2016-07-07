clear
% Import files
files = dir('*.txt');

A = zeros(1,length(files));

for i=1:length(files)
    pid = fopen(files(i).name);
    rawdata = textscan(pid, '%s %s %f %f');
    fclose(pid);
    
    date = rawdata{1}(:);
    time = rawdata{2}(:);
    offset = rawdata{3}(:);
    jitter = rawdata{4}(:);

    date = strcat(date, '_');
    date = strcat(date, time);

    date_time = datenum(date,'yyyy-mm-dd_HH:MM:SS');
    
    A(i) = subplot(length(files),1,i);
    plot(date_time, offset);
    title(files(i).name);
    dynamicDateTicks();
    

end

linkaxes([A], 'xy');

% Mark when frequency adjustments were made
freq_adj_1 = graph2d.constantline(datenum('2015-02-25_08:42:00', 'yyyy-mm-dd_HH:MM:SS'), 'Color', 'r'); % - 19780
changedependvar(freq_adj_1, 'x');
freq_adj_2 = graph2d.constantline(datenum('2015-02-27_09:23:00', 'yyyy-mm-dd_HH:MM:SS'), 'Color', 'r'); % - 167400
changedependvar(freq_adj_2, 'x');
freq_adj_3 = graph2d.constantline(datenum('2015-03-02_13:52:00', 'yyyy-mm-dd_HH:MM:SS'), 'Color', 'r'); % - 2 000 000
changedependvar(freq_adj_3, 'x');