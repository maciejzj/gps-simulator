from gps_simulator import time_match_frequency


def test_time_match_frequency_1hz_time_to_1hz_freq():
    times = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    frequency = 1
    times_after_match = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert time_match_frequency(times, frequency) == times_after_match
        

def test_time_match_frequency_0_5hz_time_to_1hz_freq():
    times = (0, 2, 4, 6, 8, 10)
    frequency = 1
    times_after_match = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert time_match_frequency(times, frequency) == times_after_match
        
    
def test_time_match_frequency_1hz_time_to_0_5hz_freq():
    times = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    frequency = 0.5
    times_after_match = (0, 2, 4, 6, 8, 10)
    assert time_match_frequency(times, frequency) == times_after_match


def test_time_match_frequency_1hz_time_to_2hz_freq():
    times = (0, 1, 2, 3, 4, 5)
    frequency = 2
    times_after_match = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0)
    assert time_match_frequency(times, frequency) == times_after_match
