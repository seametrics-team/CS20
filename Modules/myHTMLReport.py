#----------------------------------------------------------------------
# Graphics/Plotting Module
''' author: Jeff Peery '''
# date: 02/28/2008
# email: JeffPeery@yahoo.com
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Revision Log
#
# Rev   Date        Author  Description    
#----------------------------------------------------------------------

#-------------------------------------------------------------------------
# Modules
#-------------------------------------------------------------------------
import matplotlib
from myHeader import *
from os.path import exists

class Report:
    def __init__(self, tests, flow_meter, meter_label):
        #----------------------------------
        # Attributes
        #----------------------------------
        # calibration test object
        self.tests = tests
        # flow meter object
        self.flow_meter = flow_meter
        # constant value, meter type
        self.meter_label = meter_label
        
        assert type(tests) == list
        assert len(tests) > 1
        assert exists(REPORT_TEMPLATE_FILE)

    def GetTemplate(self):
        fh = open(REPORT_TEMPLATE_FILE)
        report = fh.read()
        fh.close()
        return report

    def GetReportValues(self):
        title = REPORT_TITLE
        cal_date = self.flow_meter.GetCalibrationDate()
        serial_num = str(self.flow_meter.GetSerialNumber())
        
        test_nums       = []
        per_fs_flows    = []
        water_temps     = []
        true_flow_rates = []
        k_factors       = []
        volumes         = []
        test_times      = []
        u_bias          = []
        type_B_u        = []
        total_u         = []
        
        i=1
        for test in self.tests:
            test_times.append(str(test.GetTime()))
            test_nums.append(str(i))
            per_fs_flows.append('%0.1f'%(100.0*test.GetRefFlowRate()/self.flow_meter.GetMaxFlowRate()))
            true_flow_rates.append('%0.3f'%test.GetRefFlowRate())
##            water_temps.append('%0.2f'%0.0)
            water_temps.append('%0.2f'%test.GetTemp())
            k_factors.append('%0.2f'%test.GetKFactor())
            # volume measured by MUT
            volumes.append('%0.2f'%(test.GetMUTPulseCount()/self.flow_meter.GetKFactor()))
            u_v,u_q,u_k = test.GetUncertainties()
            # deviation of k-factor from nominal
            u = 100.0*(test.GetKFactor() - self.flow_meter.GetKFactor())/self.flow_meter.GetKFactor()
            u_bias.append('%0.2f'%u)
            # convert from expanded to standard uncertainty
            type_B_u.append('%0.2f'%(u_k/2.0))
            # the coverage factor was already included in u_k, so we don't need to add it here.
            # DO NOT INCLUDE THE BIAS HERE. The bias is the %deviation from nominal k-factor. It has nothing to do
            # with the systematic component of uncertainty in the calibration system. This component is assumed zero.
            #
            # It should only come together when we decide if the flow meter is operating within 1% ONE OUR SYSTEM ONLY!!!
            total_u.append('%0.2f'%(abs(u_k)))
            i+=1
            
        return serial_num, title, self.meter_label, cal_date, test_nums, per_fs_flows, water_temps, true_flow_rates, k_factors, u_bias, type_B_u, total_u, test_times

    def CreateReport(self):
        serial_num, title, label, cal_date, test_nums, per_fs_flows, water_temps, true_flow_rates, k_factors, u_biases, type_B_us, total_us, test_times = self.GetReportValues()

        assert type(serial_num) == str
        assert type(title) == str
        assert type(label) == str
        assert type(cal_date) == str

        # strip seconds off date
        cal_date = cal_date.split(':')
        cal_date = cal_date[0]+':'+cal_date[1]
        
        # fill html template with values
        template = self.GetTemplate()
        template = template.replace('<!---nominal_k--->', '%0.2f'%self.flow_meter.GetKFactor())
        template = template.replace('<!---serial_num--->', serial_num)
        template = template.replace('<!---title--->', title)
        template = template.replace('<!---label--->', label)
        template = template.replace('<!---cal_date--->', cal_date)
        template = template.replace('<!---image src--->', REPORT_IMAGE_FOLDER+'\\'+serial_num+'.'+REPORT_FIGURE_FORMAT)
        
        rows = ''
        for i in range(len(test_nums)):
            test_num        = test_nums[i]
            per_fs_flow     = per_fs_flows[i]
            water_temp      = water_temps[i]
            true_flow_rate  = true_flow_rates[i]
            k_factor        = k_factors[i]
            type_B_u        = type_B_us[i]
            u_bias          = u_biases[i]
            total_u         = total_us[i]
            test_time       = test_times[i]
            
            assert type(test_num) == str
            assert type(per_fs_flow) == str
            assert type(water_temp) == str
            assert type(true_flow_rate) == str
            assert type(k_factor) == str
            assert type(type_B_u) == str
            assert type(u_bias) == str
            assert type(total_u) == str
            assert type(test_time) == str
            rows += """
                    <tr>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    <td><span class="bodytext">%s</span></td>
                    </tr>
                    """%(test_num, test_time, water_temp, per_fs_flow, true_flow_rate,
                         k_factor, u_bias, total_u)
            
        template = template.replace('<!---rows--->', rows)

        fh = open(str(REPORT_IMAGE_FOLDER+'\\'+serial_num+'.htm'), 'w')
        fh.write(template)
        fh.close()
