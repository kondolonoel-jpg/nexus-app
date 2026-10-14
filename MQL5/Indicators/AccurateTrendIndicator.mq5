#property copyright "KONDOLO NOEL | kondolonoel@gmail.com"
#property link      "mailto:kondolonoel@gmail.com"
#property version   "1.00"
#property description "Accurate Trend Indicator with live BUY/SELL signals and notifications."
#property indicator_chart_window
#property indicator_buffers 5
#property indicator_plots   1
#property indicator_type1   DRAW_COLOR_CANDLES
#property indicator_color1  clrGreen, clrRed
#property indicator_label1  "Trend candles"

input int    InpATRLength             = 10;        // ATR length
input double InpMultiplier            = 3.0;       // Supertrend multiplier
input bool   InpEnableMobilePush      = true;      // Send mobile push notifications
input bool   InpEnableSound           = true;      // Play a sound for each signal
input bool   InpEnableTextAlert       = true;      // Show a text alert in MetaTrader
input string InpSoundFile             = "alert.wav"; // Sound file in the terminal Sounds folder

double CandleOpenBuffer[];
double CandleHighBuffer[];
double CandleLowBuffer[];
double CandleCloseBuffer[];
double CandleColorIndexBuffer[];

double TrueRangeValues[];
double ATRValues[];
double FinalUpperBand[];
double FinalLowerBand[];
double SupertrendValues[];
int    SignalValues[];

datetime LastCalculatedBarTime   = 0;
string   SignalObjectPrefix      = "";
bool     RealtimeStateInitialized = false;
datetime RealtimeBarTime         = 0;
int      PreviousRealtimeSignal  = 0;

//+------------------------------------------------------------------+
//| Initialize the indicator                                         |
//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpATRLength < 1)
     {
      Print("ATR length must be at least 1.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(!SetIndexBuffer(0,CandleOpenBuffer,INDICATOR_DATA) ||
      !SetIndexBuffer(1,CandleHighBuffer,INDICATOR_DATA) ||
      !SetIndexBuffer(2,CandleLowBuffer,INDICATOR_DATA) ||
      !SetIndexBuffer(3,CandleCloseBuffer,INDICATOR_DATA) ||
      !SetIndexBuffer(4,CandleColorIndexBuffer,INDICATOR_COLOR_INDEX))
      return(INIT_FAILED);

   ArraySetAsSeries(CandleOpenBuffer,true);
   ArraySetAsSeries(CandleHighBuffer,true);
   ArraySetAsSeries(CandleLowBuffer,true);
   ArraySetAsSeries(CandleCloseBuffer,true);
   ArraySetAsSeries(CandleColorIndexBuffer,true);

   PlotIndexSetDouble(0,PLOT_EMPTY_VALUE,EMPTY_VALUE);
   PlotIndexSetInteger(0,PLOT_COLOR_INDEXES,2);
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,InpATRLength-1);

   SignalObjectPrefix="KN_ATI_"+
                      IntegerToString(ChartID())+"_"+
                      IntegerToString((long)GetTickCount())+"_";

   IndicatorSetString(INDICATOR_SHORTNAME,
                      StringFormat("Accurate Trend Indicator (%d, %.2f)",
                                   InpATRLength,InpMultiplier));
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Release chart objects created by this indicator                  |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(StringLen(SignalObjectPrefix)>0)
      ObjectsDeleteAll(0,SignalObjectPrefix);
  }

//+------------------------------------------------------------------+
//| Resize internal calculation arrays                               |
//+------------------------------------------------------------------+
bool ResizeInternalArrays(const int count)
  {
   if(ArrayResize(TrueRangeValues,count)!=count ||
      ArrayResize(ATRValues,count)!=count ||
      ArrayResize(FinalUpperBand,count)!=count ||
      ArrayResize(FinalLowerBand,count)!=count ||
      ArrayResize(SupertrendValues,count)!=count ||
      ArrayResize(SignalValues,count)!=count)
      return(false);

   ArraySetAsSeries(TrueRangeValues,true);
   ArraySetAsSeries(ATRValues,true);
   ArraySetAsSeries(FinalUpperBand,true);
   ArraySetAsSeries(FinalLowerBand,true);
   ArraySetAsSeries(SupertrendValues,true);
   ArraySetAsSeries(SignalValues,true);
   return(true);
  }

//+------------------------------------------------------------------+
//| True range, with high-low used when there is no previous bar      |
//+------------------------------------------------------------------+
double GetTrueRange(const int index,
                    const int rates_total,
                    const double &high[],
                    const double &low[],
                    const double &close[])
  {
   double range=high[index]-low[index];
   if(index+1<rates_total)
     {
      range=MathMax(range,MathAbs(high[index]-close[index+1]));
      range=MathMax(range,MathAbs(low[index]-close[index+1]));
     }
   return(range);
  }

//+------------------------------------------------------------------+
//| Calculate Supertrend value and crossover signal for one bar      |
//+------------------------------------------------------------------+
void CalculateTrendAt(const int index,
                      const int rates_total,
                      const double &high[],
                      const double &low[],
                      const double &close[])
  {
   FinalUpperBand[index]=EMPTY_VALUE;
   FinalLowerBand[index]=EMPTY_VALUE;
   SupertrendValues[index]=EMPTY_VALUE;
   SignalValues[index]=0;

   if(ATRValues[index]==EMPTY_VALUE)
      return;

   double source=(high[index]+low[index])*0.5;
   double basicUpper=source+InpMultiplier*ATRValues[index];
   double basicLower=source-InpMultiplier*ATRValues[index];

   bool hasPreviousClose=(index+1<rates_total);
   bool hasPreviousATR=(hasPreviousClose && ATRValues[index+1]!=EMPTY_VALUE);
   double previousLower=(hasPreviousATR ? FinalLowerBand[index+1] : 0.0);
   double previousUpper=(hasPreviousATR ? FinalUpperBand[index+1] : 0.0);

   bool keepBasicLower=(basicLower>previousLower);
   if(hasPreviousClose && close[index+1]<previousLower)
      keepBasicLower=true;

   bool keepBasicUpper=(basicUpper<previousUpper);
   if(hasPreviousClose && close[index+1]>previousUpper)
      keepBasicUpper=true;

   double currentLower=(keepBasicLower ? basicLower : previousLower);
   double currentUpper=(keepBasicUpper ? basicUpper : previousUpper);
   FinalLowerBand[index]=currentLower;
   FinalUpperBand[index]=currentUpper;

   int direction=1;
   if(hasPreviousATR)
     {
      if(SupertrendValues[index+1]==FinalUpperBand[index+1])
         direction=(close[index]>currentUpper ? -1 : 1);
      else
         direction=(close[index]<currentLower ? 1 : -1);
     }

   SupertrendValues[index]=(direction==-1 ? currentLower : currentUpper);

   if(hasPreviousATR && SupertrendValues[index+1]!=EMPTY_VALUE)
     {
      if(close[index]>SupertrendValues[index] &&
         close[index+1]<=SupertrendValues[index+1])
         SignalValues[index]=1;
      else if(close[index]<SupertrendValues[index] &&
              close[index+1]>=SupertrendValues[index+1])
         SignalValues[index]=-1;
     }
  }

//+------------------------------------------------------------------+
//| Set candle buffers; color index 0 is green and 1 is red          |
//+------------------------------------------------------------------+
void SetCandleData(const int index,
                   const int trendColor,
                   const double &open[],
                   const double &high[],
                   const double &low[],
                   const double &close[])
  {
   if(trendColor<0)
     {
      CandleOpenBuffer[index]=EMPTY_VALUE;
      CandleHighBuffer[index]=EMPTY_VALUE;
      CandleLowBuffer[index]=EMPTY_VALUE;
      CandleCloseBuffer[index]=EMPTY_VALUE;
      CandleColorIndexBuffer[index]=0.0;
      return;
     }

   CandleOpenBuffer[index]=open[index];
   CandleHighBuffer[index]=high[index];
   CandleLowBuffer[index]=low[index];
   CandleCloseBuffer[index]=close[index];
   CandleColorIndexBuffer[index]=(double)trendColor;
  }

//+------------------------------------------------------------------+
//| Calculate all history after initialization or when a new bar forms|
//+------------------------------------------------------------------+
void CalculateAllBars(const int rates_total,
                      const double &open[],
                      const double &high[],
                      const double &low[],
                      const double &close[])
  {
   double atrSeedSum=0.0;
   int atrSeedCount=0;
   double currentATR=0.0;
   bool atrReady=false;
   int persistentColor=-1;

   for(int index=rates_total-1;index>=0;index--)
     {
      TrueRangeValues[index]=GetTrueRange(index,rates_total,high,low,close);

      if(!atrReady)
        {
         atrSeedSum+=TrueRangeValues[index];
         atrSeedCount++;
         if(atrSeedCount>=InpATRLength)
           {
            currentATR=atrSeedSum/(double)InpATRLength;
            ATRValues[index]=currentATR;
            atrReady=true;
           }
         else
            ATRValues[index]=EMPTY_VALUE;
        }
      else
        {
         currentATR=((currentATR*(InpATRLength-1.0))+TrueRangeValues[index])/(double)InpATRLength;
         ATRValues[index]=currentATR;
        }

      CalculateTrendAt(index,rates_total,high,low,close);

      if(SignalValues[index]>0)
         persistentColor=0;
      else if(SignalValues[index]<0)
         persistentColor=1;

      SetCandleData(index,persistentColor,open,high,low,close);
     }
  }

//+------------------------------------------------------------------+
//| Recalculate the forming candle on each incoming tick             |
//+------------------------------------------------------------------+
void CalculateCurrentBar(const int rates_total,
                         const double &open[],
                         const double &high[],
                         const double &low[],
                         const double &close[])
  {
   TrueRangeValues[0]=GetTrueRange(0,rates_total,high,low,close);

   if(rates_total<InpATRLength)
      ATRValues[0]=EMPTY_VALUE;
   else if(rates_total>1 && ATRValues[1]!=EMPTY_VALUE)
      ATRValues[0]=((ATRValues[1]*(InpATRLength-1.0))+TrueRangeValues[0])/(double)InpATRLength;
   else
     {
      double seedSum=0.0;
      for(int index=0;index<InpATRLength;index++)
         seedSum+=TrueRangeValues[index];
      ATRValues[0]=seedSum/(double)InpATRLength;
     }

   CalculateTrendAt(0,rates_total,high,low,close);

   int persistentColor=-1;
   if(rates_total>1 && CandleOpenBuffer[1]!=EMPTY_VALUE)
      persistentColor=(int)CandleColorIndexBuffer[1];

   if(SignalValues[0]>0)
      persistentColor=0;
   else if(SignalValues[0]<0)
      persistentColor=1;

   SetCandleData(0,persistentColor,open,high,low,close);
  }

//+------------------------------------------------------------------+
//| Build a stable chart-object name for a signal label              |
//+------------------------------------------------------------------+
string SignalObjectBaseName(const int signal,const datetime barTime)
  {
   string side=(signal>0 ? "B_" : "S_");
   return(SignalObjectPrefix+side+IntegerToString((long)barTime));
  }

//+------------------------------------------------------------------+
//| Draw a filled signal label with white BUY/SELL text               |
//+------------------------------------------------------------------+
void DrawSignalLabel(const datetime barTime,
                     const double barHigh,
                     const double barLow,
                     const double atr,
                     const int signal)
  {
   if(signal==0 || atr==EMPTY_VALUE)
      return;

   double gap=MathMax(atr*0.12,3.0*_Point);
   double boxHeight=MathMax(atr*0.22,8.0*_Point);
   double topPrice=0.0;
   double bottomPrice=0.0;

   if(signal>0)
     {
      topPrice=barLow-gap;
      bottomPrice=topPrice-boxHeight;
     }
   else
     {
      bottomPrice=barHigh+gap;
      topPrice=bottomPrice+boxHeight;
     }

   int periodSeconds=PeriodSeconds(_Period);
   if(periodSeconds<2)
      periodSeconds=60;
   int halfSpan=periodSeconds/3;
   if(halfSpan<1)
      halfSpan=1;

   datetime leftTime=barTime-halfSpan;
   datetime rightTime=barTime+halfSpan;
   string baseName=SignalObjectBaseName(signal,barTime);
   string boxName=baseName+"_BG";
   string textName=baseName+"_TEXT";
   color labelColor=(signal>0 ? clrGreen : clrRed);

   if(ObjectFind(0,boxName)<0)
      ObjectCreate(0,boxName,OBJ_RECTANGLE,0,leftTime,topPrice,rightTime,bottomPrice);
   else
     {
      ObjectMove(0,boxName,0,leftTime,topPrice);
      ObjectMove(0,boxName,1,rightTime,bottomPrice);
     }
   ObjectSetInteger(0,boxName,OBJPROP_COLOR,labelColor);
   ObjectSetInteger(0,boxName,OBJPROP_FILL,true);
   ObjectSetInteger(0,boxName,OBJPROP_BACK,false);
   ObjectSetInteger(0,boxName,OBJPROP_STYLE,STYLE_SOLID);
   ObjectSetInteger(0,boxName,OBJPROP_WIDTH,1);
   ObjectSetInteger(0,boxName,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,boxName,OBJPROP_SELECTED,false);
   ObjectSetInteger(0,boxName,OBJPROP_HIDDEN,true);

   if(ObjectFind(0,textName)<0)
      ObjectCreate(0,textName,OBJ_TEXT,0,barTime,(topPrice+bottomPrice)*0.5);
   else
      ObjectMove(0,textName,0,barTime,(topPrice+bottomPrice)*0.5);
   ObjectSetString(0,textName,OBJPROP_TEXT,(signal>0 ? "BUY" : "SELL"));
   ObjectSetString(0,textName,OBJPROP_FONT,"Arial");
   ObjectSetInteger(0,textName,OBJPROP_FONTSIZE,8);
   ObjectSetInteger(0,textName,OBJPROP_ANCHOR,ANCHOR_CENTER);
   ObjectSetInteger(0,textName,OBJPROP_COLOR,clrWhite);
   ObjectSetInteger(0,textName,OBJPROP_BACK,false);
   ObjectSetInteger(0,textName,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,textName,OBJPROP_SELECTED,false);
   ObjectSetInteger(0,textName,OBJPROP_HIDDEN,true);
  }

//+------------------------------------------------------------------+
//| Remove a label for one side of a bar                              |
//+------------------------------------------------------------------+
void DeleteSignalLabel(const int signal,const datetime barTime)
  {
   string baseName=SignalObjectBaseName(signal,barTime);
   ObjectDelete(0,baseName+"_BG");
   ObjectDelete(0,baseName+"_TEXT");
  }

//+------------------------------------------------------------------+
//| Send all enabled notifications immediately when a live cross occurs|
//+------------------------------------------------------------------+
void SendSignalNotifications(const int signal,
                            const datetime barTime,
                            const double signalPrice)
  {
   string direction=(signal>0 ? "BUY" : "SELL");
   string timeframe=EnumToString((ENUM_TIMEFRAMES)_Period);
   string message=StringFormat("Accurate Trend Indicator: %s %s %s | %s | Close %s",
                               direction,
                               _Symbol,
                               timeframe,
                               TimeToString(barTime,TIME_DATE|TIME_MINUTES),
                               DoubleToString(signalPrice,_Digits));

   if(InpEnableTextAlert)
      Alert(message);

   if(InpEnableMobilePush && !SendNotification(message))
     {
      int errorCode=GetLastError();
      PrintFormat("Mobile push notification failed (error %d). Check terminal notification settings.",
                  errorCode);
     }

   if(InpEnableSound && StringLen(InpSoundFile)>0 && !PlaySound(InpSoundFile))
      PrintFormat("Could not play sound file '%s'. Check the terminal Sounds folder.",InpSoundFile);
  }

//+------------------------------------------------------------------+
//| Detect live signal transitions and prevent per-tick duplicates    |
//+------------------------------------------------------------------+
void ProcessRealtimeNotifications(const datetime &time[],const double &close[])
  {
   if(!RealtimeStateInitialized)
     {
      RealtimeBarTime=time[0];
      PreviousRealtimeSignal=SignalValues[0];
      RealtimeStateInitialized=true;
      return;
     }

   if(time[0]!=RealtimeBarTime)
     {
      RealtimeBarTime=time[0];
      PreviousRealtimeSignal=0;
     }

   int currentSignal=SignalValues[0];
   if(currentSignal!=0 && currentSignal!=PreviousRealtimeSignal)
      SendSignalNotifications(currentSignal,time[0],close[0]);

   PreviousRealtimeSignal=currentSignal;
  }

//+------------------------------------------------------------------+
//| Main calculation                                                  |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
   if(rates_total<1)
      return(0);

   ArraySetAsSeries(time,true);
   ArraySetAsSeries(open,true);
   ArraySetAsSeries(high,true);
   ArraySetAsSeries(low,true);
   ArraySetAsSeries(close,true);

   if(!ResizeInternalArrays(rates_total))
      return(prev_calculated);

   bool fullRecalculation=(prev_calculated==0 ||
                           LastCalculatedBarTime==0 ||
                           time[0]!=LastCalculatedBarTime ||
                           prev_calculated>rates_total);

   if(fullRecalculation)
     {
      CalculateAllBars(rates_total,open,high,low,close);
      ObjectsDeleteAll(0,SignalObjectPrefix);
      for(int index=rates_total-1;index>=0;index--)
        {
         if(SignalValues[index]!=0)
            DrawSignalLabel(time[index],high[index],low[index],ATRValues[index],SignalValues[index]);
        }
     }
   else
     {
      CalculateCurrentBar(rates_total,open,high,low,close);
      if(SignalValues[0]!=0)
         DrawSignalLabel(time[0],high[0],low[0],ATRValues[0],SignalValues[0]);
      else
        {
         DeleteSignalLabel(1,time[0]);
         DeleteSignalLabel(-1,time[0]);
        }
     }

   LastCalculatedBarTime=time[0];
   ProcessRealtimeNotifications(time,close);
   return(rates_total);
  }
//+------------------------------------------------------------------+
