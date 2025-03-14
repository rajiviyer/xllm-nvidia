"use client";
import { useForm } from "react-hook-form";
import { FormType } from "@/lib/utils/types";
import { useState } from "react";
import React from "react";
import OptionButton from "./OptionButton";
import Button from "./Button";
import { queries } from "@/lib/utils/data";
import { ResultDocProps } from "@/lib/utils/types";
import { Slider } from "@/components/ui/slider";
import Link from "next/link";
import Image from "next/image";

const ParamForm: React.FC<ResultDocProps> = ({ setResult }) => {
  const { register, handleSubmit } = useForm<FormType>();
  // const [byPassList, setByPassList] = useState(false);
  const [seedQuery, setSeedQuery] = useState(true);
  const [useStem, setUseStem] = useState(false);
  const [distill, setDistill] = useState(false);
  const [isDebugTooltipVisible, setIsDebugTooltipVisible] = useState(false);

  // State to track the height of the textarea
  const [heightIgnoreList, setHeightIgnoreList] = useState<string>("auto");
  const [heightQueryText, setHeightQueryText] = useState<string>("auto");

  const defaultFormData = {
    useStem: true,
    beta: 1.0,
    queryText: queries[0],
    distill: true,
    maxTokenCount: 500,
    nresults: 15
  };

  const minFormData = {
    useStem: true,
    beta: 0.5,
    queryText: queries[0],
    distill: false,
    maxTokenCount: 2,
    nresults: 15
  };

  const [formData, setFormData] = useState(defaultFormData);

  const handleInputChange = (
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = event.target;
    console.log(name, value);

    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleOptionButtonClickUseStem = (option: boolean) => {
    console.log("use_stem", option);
    setUseStem(option);
  };

  const handleOptionButtonClickDistill = (option: boolean) => {
    // console.log("custom pmi", option);
    setDistill(option);
  };  
  // const handleOptionButtonClickIgnoreList = (option: boolean) => {
  //   // console.log("bypass", option);
  //   setByPassList(option);
  // };

  const handleOptionButtonClickQuery = (option: boolean) => {
    // console.log("query", option);
    setSeedQuery(option);
  };

  const handleResetButtonClick = () => {
    window.location.reload(); // Refresh the page
  };

  const showDebugTooltip = () => {
    setIsDebugTooltipVisible(true);
  };

  const hideDebugTooltip = () => {
    setIsDebugTooltipVisible(false);
  };

  const handleDebugButtonClick = () => {
    console.log(`Debug formdata: ${JSON.stringify(formData)}`); // Log the formData);
    console.log(`Debug minformdata: ${JSON.stringify(minFormData)}`); // Log the minformData);
    setFormData(() => ({
      ...minFormData,
      queryText:
        formData.queryText?.length > 0 ? formData.queryText : queries[0],
    }));
  };

  // Handle focus event to increase the height
  const handleFocusIgnoreList = () => {
    setHeightIgnoreList("150px");
  };

  const handleFocusQueryText = () => {
    setHeightQueryText("150px");
  };

  // Handle blur event to reset the height
  const handleBlurIgnoreList = () => {
    setHeightIgnoreList("auto"); // Reset to original size (or you can specify a fixed height)
  };

  const handleBlurQueryText = () => {
    setHeightQueryText("auto"); // Reset to original size (or you can specify a fixed height)
  };

  // const retrieveDocs = async (data: Object) => {
  const retrieveDocs = async () => {
    const data = {
      ...formData,
      useStem: useStem,
      distill: distill
    };

    if (data) {
      console.log(data);
    } else {
      console.log("No data found");
    }
    try {
      const url = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${url}/api/docs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const result_data = await response.json();
      // print length of the result list

      if (result_data) {
        // console.log(result_data.length);
        setResult(result_data);
      } else {
        console.log("No result found");
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="w-full flex flex-col h-screen justify-between">
      <div className="container p-1 border border-bondingai_input_border/[0.60] rounded-md mt-2">
        <h2 className="text-slate-100 mb-3 text-center">Parameters</h2>
        <form onSubmit={handleSubmit(retrieveDocs)} className="w-full">
          <div className="flex flex-wrap mb-7">
            <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
              <label className="text-bondingai_input_label text-sm" htmlFor="use_stem">
                Use Stem
              </label>
              <OptionButton
                handleOptionButtonClick={handleOptionButtonClickUseStem}
                selectedOption={useStem}
                option1="Yes"
                option2="No"
              />
            </div>
            <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
              <label className="text-bondingai_input_label text-sm" htmlFor="distill">
                Distill
              </label>
              <OptionButton
                handleOptionButtonClick={handleOptionButtonClickDistill}
                selectedOption={distill}
                option1="Yes"
                option2="No"
              />
            </div>
          </div>
          <div className="flex flex-wrap mb-7">
            <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
              <label
                className="text-bondingai_input_label text-sm"
                htmlFor="beta"
              >
                Beta Value
              </label>
              <input
                type="number"
                {...register("beta", { required: true })}
                value={formData.beta}
                onChange={(event) => handleInputChange(event)}
                min="0.5"
                max="1.0"
                step="0.1"
                className="bg-bondingai_primary border border-bondingai_input_border text-slate-300 text-sm rounded-md w-full p-1"
              />
            </div>
            <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
              <label className="text-bondingai_input_label text-sm" htmlFor="nresults">
              nResults &nbsp;
              </label>
              <input
                type="number"
                {...register("nresults", { required: true })}
                value={formData.nresults}
                onChange={(event) => handleInputChange(event)}
                min="4"
                max="15"
                step="1"
                className="bg-bondingai_primary border border-bondingai_input_border text-slate-300 text-sm rounded-md w-full p-1"
              />
            </div>
          </div>
          <div className="flex flex-wrap mb-7">
            <div className="w-full px-3 mb-6 md:mb-0">
                <label className="text-bondingai_input_label text-sm" htmlFor="maxTokenCount">
                  Max. Token Count
                </label>
                <input
                  type="number"
                  {...register("maxTokenCount", { required: true })}
                  value={formData.maxTokenCount}
                  min="2"
                  step="1"
                  onChange={(event) => handleInputChange(event)}
                  className="bg-bondingai_primary border border-bondingai_input_border text-slate-300 text-sm rounded-md w-full p-1"
                />
            </div>
          </div>
          <div className="flex flex-wrap mb-11">
            <div className="w-full md:w-1/2 px-3 mb-10 md:mb-0">
              <label className="text-bondingai_input_label text-sm">Query</label>
              <OptionButton
                handleOptionButtonClick={handleOptionButtonClickQuery}
                selectedOption={seedQuery}
                option1="Seeded"
                option2="Custom"
              />
            </div>
            {seedQuery === true ? (
              <div className="w-full md:w-1/2 px-3 mb-10 md:mb-0">
                <br />
                <select
                  {...register("queryText", { required: true })}
                  className="bg-bondingai_primary border border-bondingai_input_border text-slate-300 text-sm h-2/3 rounded-md w-full p-1"
                  onChange={(event) => handleInputChange(event)}
                >
                  {queries.map((query, index) => {
                    return (
                      <option key={index} value={query}>
                        {query}
                      </option>
                    );
                  })}
                </select>
              </div>
            ) : (
              <div className="w-full md:w-1/2 px-3 mb-10 md:mb-0">
                <br />
                <textarea
                  {...register("queryText", { required: true })}
                  value={formData.queryText}
                  onChange={(event) => handleInputChange(event)}
                  placeholder="parameterized datasets map tables sql server..."
                  className="bg-bondingai_primary border border-bondingai_input_border text-slate-300 text-sm rounded-md w-40 p-1 transition-all duration-300 ease-in-out"
                  style={{ height: `${heightQueryText}` }} // Apply dynamic height
                  onFocus={handleFocusQueryText}
                  onBlur={handleBlurQueryText}
                />
              </div>
            )}
          </div>
          <div className="flex flex-row justify-center gap-4 px-3 mt-15">
            <Button buttonType="submit">Retrieve Docs</Button>
            {/* <Link href="/" passHref onClick={handleResetButtonClick}> */}
            <Button buttonType="button" onClick={handleResetButtonClick}>
              Reset
            </Button>
            {/* </Link> */}
            <div className="relative inline-block group">
              <Button buttonType="button" onClick={handleDebugButtonClick}>
                Debug
              </Button>
              <div
                id="tooltip-debug"
                data-tooltip-placement="top"
                className="absolute z-50 invisible opacity-0 group-hover:visible group-hover:opacity-100 break-words rounded-lg bg-black py-1.5 px-3 font-sans text-sm font-normal text-white top-[-60px] left-[-40px] transform transition-opacity duration-300 w-40"
              >
                Debug resets numeric inputs to their minimum values.
              </div>
            </div>
          </div>
        </form>
      </div>
      <div className="space-y-10 rtl:space-y-reverse">
          <Image src="/xllm_tagline.png" alt="xllm tagline" width={75} height={25} />
      </div>
    </div>
  );
};
export default ParamForm;
